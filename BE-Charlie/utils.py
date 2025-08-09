import base64
import hashlib
import hmac
import re
import time
from datetime import date

import oss2
import requests

from config import LOGIN_SECRET, OSS_ACCESS_KEY_ID, OSS_ENDPOINT, OSS_BUCKET_NAME, OSS_ACCESS_KEY_SECRET, PREFIX
from models import Session, PlaceBeenTo, TravelPhoto


def encode(input_string):
    byteString = input_string.encode('utf-8')
    base64_bytes = base64.b64encode(byteString)
    encoded_string = base64_bytes.decode()
    return encoded_string


def decode(encoded_string):
    try:
        base64_bytes = encoded_string.encode('utf-8')
        byte_string = base64.b64decode(base64_bytes)
        decoded_string = byte_string.decode()
    except Exception:
        return None
    return decoded_string


def calc_signature(message):
    secret = LOGIN_SECRET.encode('utf-8')
    message = str(message).encode('utf-8')
    signature = hmac.new(secret, message, hashlib.sha512).hexdigest()
    return signature


def generate_sessionid(user_id):
    timestamp = str(int(time.time()))
    signature = calc_signature(str(user_id))
    sessionid = f"userId={user_id}&timestamp={timestamp}&signature={signature}&algorithm=sha512"
    return encode(sessionid)


def check_signature(signature, message):
    secret = LOGIN_SECRET.encode('utf-8')
    message = str(message).encode('utf-8')
    correct_sig = hmac.new(secret, message, hashlib.sha512).hexdigest()
    return hmac.compare_digest(signature, correct_sig)


def check_sessionid(sessionid):
    decoded_sessionid = decode(sessionid)
    if not decoded_sessionid:
        return {}
    pattern = rf"^userId=(\d+)&timestamp=(\d+)&signature=(.+)&algorithm=sha512$"  # 必须用()包含住捕获组才能被match.group捕获
    match = re.match(pattern, decoded_sessionid)
    if not match:
        return {}
    user_id = match.group(1)
    timestamp = match.group(2)
    signature = match.group(3)
    if not check_signature(signature, user_id):  # 签名无效
        return {}
    if time.time() - float(timestamp) > 10800:  # 3小时有效
        return {}
    return {
        "user_id": int(user_id),
        "timestamp": timestamp
    }


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


def store_photos_from_oss_by_travelId(travelId: int):
    session = Session()
    travel = session.get(PlaceBeenTo, travelId)
    city = travel.city_ENG
    pref = f'images/travel/{city.lower().replace(" ", "")}/'
    AUTH = oss2.Auth(OSS_ACCESS_KEY_ID, OSS_ACCESS_KEY_SECRET)
    BUCKET = oss2.Bucket(AUTH, OSS_ENDPOINT, OSS_BUCKET_NAME)
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


if __name__ == '__main__':
    # get_footprint_from_ctrip()
    store_all_photos()
