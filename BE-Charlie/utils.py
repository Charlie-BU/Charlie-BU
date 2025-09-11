import base64
import hashlib
import hmac
import time
from datetime import date
import oss2
import requests 
import json
import uuid
import os

from config import LOGIN_SECRET, SESSION_EXPIRE_SECONDS, OSS_ACCESS_KEY_ID, OSS_ENDPOINT, OSS_BUCKET_NAME, OSS_ACCESS_KEY_SECRET, PREFIX
from models import Session, PlaceBeenTo, TravelPhoto
from redis_settings import redis_client


AUTH = oss2.Auth(OSS_ACCESS_KEY_ID, OSS_ACCESS_KEY_SECRET)
BUCKET = oss2.Bucket(AUTH, OSS_ENDPOINT, OSS_BUCKET_NAME)


def generate_sessionid(user_id):
    # 通过uuid，限制单一设备登录
    session_uuid = uuid.uuid4().hex
    # 写入 redis，TTL = 会话过期时间
    redis_client.setex(f"user_id:{user_id}", SESSION_EXPIRE_SECONDS, session_uuid)
    payload = {
        "user_id": user_id,
        "timestamp": int(time.time()),
        "session_uuid": session_uuid,
        "algorithm": "sha512",
    }
    payload_str = json.dumps(payload, separators=(',', ':'))
    signature = hmac.new(LOGIN_SECRET, payload_str.encode(), hashlib.sha512).hexdigest()
    sessionid = base64.urlsafe_b64encode(f"{payload_str}.{signature}".encode()).decode()
    return sessionid


def check_sessionid(sessionid):
    try:
        decoded = base64.urlsafe_b64decode(sessionid.encode()).decode()
        payload_str, signature = decoded.rsplit('.', 1)
        expected_sig = hmac.new(LOGIN_SECRET, payload_str.encode(), hashlib.sha512).hexdigest()
       
        if not hmac.compare_digest(signature, expected_sig):
            return {}  # 签名无效
        payload = json.loads(payload_str)
        
        if not {"user_id", "timestamp", "session_uuid", "algorithm"} <= payload.keys():
            print("字段缺失")
            return {}
        if payload.get("algorithm") != "sha512":
            print("算法不匹配")
            return {}
        if time.time() - int(payload["timestamp"]) > SESSION_EXPIRE_SECONDS:
            print("sessionid 已过期")
            return {}

        # 检查 session_uuid
        nonce_key = f"user_id:{payload['user_id']}"
        if not redis_client.exists(nonce_key):
            print("session_uuid 不存在")
            return {}
        session_uuid = redis_client.get(nonce_key).decode()
        if session_uuid != payload['session_uuid']:
            print("session_uuid 不匹配")
            return {}
        
        # nonce 防重放：不能加，会导致sessionid变为一次性
        # nonce_key = f"nonce:{payload['nonce']}"
        # if redis_client.exists(nonce_key):
        #     print("nonce 已存在")
        #     return {}
        # else:
        #     # 第一次见到这个 nonce，写入 Redis，TTL = 剩余有效时间
        #     ttl = max(0, SESSION_EXPIRE_SECONDS - (time.time() - int(payload["timestamp"])))
        #     if ttl > 0:
        #         redis_client.setex(nonce_key, int(ttl), 1)
        #     else:
        #         print("ttl 小于 0")
        #         return {}

        return {
            "user_id": int(payload["user_id"]),
            "timestamp": payload["timestamp"],
        }
    
    except Exception:
        return {}


def parse_cookie_string(cookie_string):
    if not cookie_string:
        return {}
    cookies = {}
    for cookie in cookie_string.split(";"):
        key, value = cookie.strip().split("=", 1)
        cookies[key] = value
    return cookies


def normalize_city_name(name):
    if not name.endswith('市') and name not in ['香港', '澳门', '台湾']:
        return name + '市'
    return name


def extract_date(visitDate):
    return date(visitDate['year'], visitDate['month'], visitDate['day'])


def insert_new_places(data: dict):
    session = Session()
    seen_cities = set()
    for trip in data.get('userTripList', []):
        city_raw = trip['destinationName']
        city = normalize_city_name(city_raw)

        # 去重：有的城市会出现多次
        if city in seen_cities:
            continue
        seen_cities.add(city)

        exists = session.query(PlaceBeenTo).filter_by(city=city).first()
        if exists:
            continue

        visit_date = extract_date(trip['visitDate'])
        # country = get_country_by_city(city_raw)
        # country_ENG = pycountry.countries.get(name=country).name if pycountry.countries.get(name=country) else "Unknown"

        new_place = PlaceBeenTo(
            city=city,
            city_ENG="",
            dateStart=visit_date
        )
        session.add(new_place)

    session.commit()
    session.close()


def get_footprint_from_ctrip():
    URL = "https://m.ctrip.com/restapi/soa2/14185/getTripList.json"
    body = {
        "head": {
            "auth": "828F72FBB789F6AEF3DD602E8D8C1DB96294D94B665569837B50B93F6B8A7D2D",
            "extension": []
        }
    }
    try:
        res = requests.post(URL, json=body)
        insert_new_places(res.json())
    except Exception as e:
        print(e)


# 获取阿里云OSS中的旅行照片，并存到数据库
def store_photos_from_oss_by_travelId(travelId: int):
    session = Session()
    travel = session.get(PlaceBeenTo, travelId)
    city = travel.city_ENG
    pref = f'images/travel/{city.lower().replace(" ", "")}/'
    for obj in oss2.ObjectIterator(BUCKET, prefix=pref):
        url = PREFIX + obj.key
        if url.endswith('.jpg') or url.endswith('.png') or url.endswith('.jpeg'):
            exist_count = session.query(TravelPhoto).filter_by(url=url).count()
            if exist_count >= 1:
                continue
            new_photo = TravelPhoto(url=url, travelId=travelId)
            session.add(new_photo)
    session.commit()
    session.close()


def store_all_photos():
    session = Session()
    travel_ids = [tid for (tid,) in session.query(PlaceBeenTo.id)]
    for travel_id in travel_ids:
        photo_count = session.query(TravelPhoto).filter(TravelPhoto.travelId == travel_id).count()
        if photo_count >= 1:
            continue
        try:
            store_photos_from_oss_by_travelId(travel_id)
        except Exception:
            print(f"Failed to store photos for travel {travel_id}")
            continue
    session.close()


"""
优化前的问题：
- 需要创建临时目录和文件
- 写入文件到磁盘再读取
- 需要手动删除临时文件
- 代码冗长，涉及文件I/O操作
"""
# def upload_file_to_OSS(file_name: str, file_binary: bytes, oss_folder: str):
#     temp_dir = os.path.join(os.getcwd(), 'tmp')  # 工作目录创建 'tmp' 文件夹
#     os.makedirs(temp_dir, exist_ok=True)
#     temp_path = os.path.join(temp_dir, file_name)  # 临时文件路径
#     with open(temp_path, 'wb') as f:
#         f.write(file_binary)
#     oss_path = f'/{oss_folder}/{file_name}'
#     with open(temp_path, 'rb') as fileobj:
#         BUCKET.put_object(oss_path, fileobj)
#     # 文件URL
#     file_url = f'https://{OSS_BUCKET_NAME}.{OSS_ENDPOINT}/{oss_path}'
#     # 删除临时文件
#     os.remove(temp_path)
#     return file_url


def upload_file_to_OSS(file_name: str, file_binary: bytes, oss_folder: str):
    # 直接传二进制数据即可，无需创建临时文件
    oss_path = f'{oss_folder}/{file_name}'
    BUCKET.put_object(oss_path, file_binary)
    file_url = f'https://{OSS_BUCKET_NAME}.{OSS_ENDPOINT}/{oss_path}'
    return file_url


if __name__ == '__main__':
    # get_footprint_from_ctrip()
    store_all_photos()
