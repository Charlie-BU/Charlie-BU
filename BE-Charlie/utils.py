import base64
import hashlib
import hmac
import time
from datetime import date
from tkinter import SE
import oss2
import requests 
import json
import uuid

from config import LOGIN_SECRET, SESSION_EXPIRE_SECONDS, OSS_ACCESS_KEY_ID, OSS_ENDPOINT, OSS_BUCKET_NAME, OSS_ACCESS_KEY_SECRET, PREFIX
from models import *
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


def add_activitys():
    activities = [
        {"title": "一起看雪", "title_ENG": "Watch Snow Together"},
        {"title": "一起看海", "title_ENG": "Watch the Sea Together"},
        {"title": "手牵手逛街", "title_ENG": "Hold Hands and Go Shopping"},
        {"title": "喂我吃东西", "title_ENG": "Feed Me Food"},
        {"title": "一起堆雪人", "title_ENG": "Build a Snowman Together"},
        {"title": "一起坐摩天轮", "title_ENG": "Ride the Ferris Wheel Together"},
        {"title": "一起恶作剧", "title_ENG": "Play Pranks Together"},
        {"title": "一起进鬼屋", "title_ENG": "Enter a Haunted House Together"},
        {"title": "吃同一杯冰淇淋", "title_ENG": "Share the Same Ice Cream"},
        {"title": "一起搬东西", "title_ENG": "Move Things Together"},
        {"title": "一起布置我们的小窝", "title_ENG": "Decorate Our Little Nest Together"},
        {"title": "一起看日出", "title_ENG": "Watch the Sunrise Together"},
        {"title": "半夜一起看恐怖片", "title_ENG": "Watch Horror Movies Together at Midnight"},
        {"title": "送我一束花", "title_ENG": "Give Me a Bouquet of Flowers"},
        {"title": "为我做顿饭", "title_ENG": "Cook a Meal for Me"},
        {"title": "牵着我的手过马路", "title_ENG": "Hold My Hand While Crossing the Street"},
        {"title": "一起看日落", "title_ENG": "Watch the Sunset Together"},
        {"title": "一起数星星", "title_ENG": "Count Stars Together"},
        {"title": "一起洗衣服", "title_ENG": "Do Laundry Together"},
        {"title": "背靠背听同一首曲子", "title_ENG": "Listen to the Same Song Back to Back"},
        {"title": "在朋友面前介绍我", "title_ENG": "Introduce Me to Friends"},
        {"title": "把肩膀借给我靠", "title_ENG": "Let Me Lean on Your Shoulder"},
        {"title": "为我擦眼泪", "title_ENG": "Wipe Away My Tears"},
        {"title": "为我唱首歌", "title_ENG": "Sing a Song for Me"},
        {"title": "为我写篇日记", "title_ENG": "Write a Diary Entry for Me"},
        {"title": "在大街上背我", "title_ENG": "Carry Me on Your Back in the Street"},
        {"title": "随叫随到", "title_ENG": "Be Available Whenever I Call"},
        {"title": "一起看球赛", "title_ENG": "Watch Sports Games Together"},
        {"title": "比赛啃西瓜", "title_ENG": "Have a Watermelon Eating Contest"},
        {"title": "一起捏泥人", "title_ENG": "Make Clay Figures Together"},
        {"title": "一起没形象地大叫", "title_ENG": "Scream Wildly Together"},
        {"title": "一起熬夜玩游戏", "title_ENG": "Stay Up All Night Playing Games"},
        {"title": "比赛喝酒", "title_ENG": "Have a Drinking Contest"},
        {"title": "早晨一起刷牙", "title_ENG": "Brush Teeth Together in the Morning"},
        {"title": "一起发呆", "title_ENG": "Zone Out Together"},
        {"title": "一起过我们的纪念日", "title_ENG": "Celebrate Our Anniversary Together"},
        {"title": "一起对着流星许相同的愿望", "title_ENG": "Make the Same Wish on a Shooting Star"},
        {"title": "一起折许愿星", "title_ENG": "Fold Wishing Stars Together"},
        {"title": "一起做蛋糕", "title_ENG": "Bake a Cake Together"},
        {"title": "学对方说话", "title_ENG": "Imitate Each Other's Speech"},
        {"title": "当一天陌生人", "title_ENG": "Pretend to Be Strangers for a Day"},
        {"title": "把你欺负的对我没辙", "title_ENG": "Tease You Until You Give Up"},
        {"title": "讲一夜电话", "title_ENG": "Talk on the Phone All Night"},
        {"title": "为我剪指甲", "title_ENG": "Trim My Nails for Me"},
        {"title": "一起养只小狗", "title_ENG": "Raise a Puppy Together"},
        {"title": "一起拍照片", "title_ENG": "Take Photos Together"},
        {"title": "一起骑脚踏车", "title_ENG": "Ride Bicycles Together"},
        {"title": "戴同一条围巾", "title_ENG": "Share the Same Scarf"},
        {"title": "戴同一双手套", "title_ENG": "Share the Same Pair of Gloves"},
        {"title": "讲故事哄我睡觉", "title_ENG": "Tell Me Stories to Help Me Sleep"},
        {"title": "一起吃棉花糖", "title_ENG": "Eat Cotton Candy Together"},
        {"title": "一起去K歌", "title_ENG": "Go Karaoke Together"},
        {"title": "一起淋雨", "title_ENG": "Get Caught in the Rain Together"},
        {"title": "一起面对所有难堪", "title_ENG": "Face All Embarrassments Together"},
        {"title": "一起爬山", "title_ENG": "Climb Mountains Together"},
        {"title": "一起露营", "title_ENG": "Go Camping Together"},
        {"title": "一起晨练", "title_ENG": "Do Morning Exercises Together"},
        {"title": "一起傻笑", "title_ENG": "Laugh Silly Together"},
        {"title": "一起吃路边摊", "title_ENG": "Eat Street Food Together"},
        {"title": "一起去孤儿院送礼物", "title_ENG": "Visit Orphanage and Give Gifts Together"},
        {"title": "穿情侣装显摆", "title_ENG": "Wear Matching Outfits and Show Off"},
        {"title": "一起玩牌", "title_ENG": "Play Cards Together"},
        {"title": "一起吃米线到吐", "title_ENG": "Eat Rice Noodles Until We're Sick"},
        {"title": "一起踩马路到脚软", "title_ENG": "Walk the Streets Until Our Feet Hurt"},
        {"title": "一起去医院看婴儿", "title_ENG": "Visit Hospital to See Babies Together"},
        {"title": "一起去海南的天涯海角", "title_ENG": "Visit Tianya Haijiao in Hainan Together"},
        {"title": "咬一下你的脸颊", "title_ENG": "Bite Your Cheek Gently"},
        {"title": "每天说晚安", "title_ENG": "Say Good Night Every Day"},
        {"title": "一起看电影", "title_ENG": "Watch Movies Together"},
        {"title": "一起种花", "title_ENG": "Plant Flowers Together"},
        {"title": "比赛吹牛", "title_ENG": "Have a Bragging Contest"},
        {"title": "一起见对方的朋友", "title_ENG": "Meet Each Other's Friends Together"},
        {"title": "一起吃自助餐", "title_ENG": "Eat at a Buffet Together"},
        {"title": "一起荡秋千", "title_ENG": "Swing on Swings Together"},
        {"title": "一起做鬼脸", "title_ENG": "Make Funny Faces Together"},
        {"title": "一起走遍世界各地", "title_ENG": "Travel Around the World Together"},
        {"title": "一起数钱", "title_ENG": "Count Money Together"},
        {"title": "一起扎气球赢奖品", "title_ENG": "Pop Balloons to Win Prizes Together"},
        {"title": "站在马路的两侧大喊", "title_ENG": "Shout from Opposite Sides of the Street"},
        {"title": "看你打场球赛", "title_ENG": "Watch You Play a Game"},
        {"title": "一起看演唱会", "title_ENG": "Attend Concerts Together"},
        {"title": "一起沿铁轨", "title_ENG": "Walk Along Railway Tracks Together"},
        {"title": "一起挤公车", "title_ENG": "Squeeze into Crowded Buses Together"},
        {"title": "一起放风筝", "title_ENG": "Fly Kites Together"},
        {"title": "一起去普罗旺斯看花田", "title_ENG": "Visit Provence Flower Fields Together"},
        {"title": "趁你睡觉偷亲你一下", "title_ENG": "Steal a Kiss While You're Sleeping"},
        {"title": "一起放孔明灯", "title_ENG": "Release Sky Lanterns Together"},
        {"title": "起钓鱼", "title_ENG": "Go Fishing Together"},
        {"title": "一起下棋", "title_ENG": "Play Chess Together"},
        {"title": "一起在烈日下暴晒", "title_ENG": "Bask in the Scorching Sun Together"},
        {"title": "手机铃声设置成对方的声音", "title_ENG": "Set Phone Ringtone to Each Other's Voice"},
        {"title": "每天为对方留言", "title_ENG": "Leave Messages for Each Other Daily"},
        {"title": "一起捏对方的脸", "title_ENG": "Pinch Each Other's Cheeks"},
        {"title": "比赛各种各样的事", "title_ENG": "Compete in All Kinds of Things"},
        {"title": "一起看烟火", "title_ENG": "Watch Fireworks Together"},
        {"title": "在树下埋下我们的约定", "title_ENG": "Bury Our Promise Under a Tree"},
        {"title": "去海边放漂流瓶", "title_ENG": "Release Message Bottles at the Beach"},
        {"title": "拍一次婚纱照", "title_ENG": "Take Wedding Photos Once"},
        {"title": "白头偕老", "title_ENG": "Grow Old Together"}
    ]
    with Session() as session:
        for activity in activities:
            new_activity = Activity(
                title=activity["title"],
                title_ENG=activity["title_ENG"],
            )
            session.add(new_activity)
        session.commit()
        print("Activities added")
        

def add_():
    with Session() as session:
        user = Admin(name="小迪", password=Admin.hash_password("wangdi20050202"))
        session.add(user)
        session.commit()
        print("success")
        

if __name__ == '__main__':
    # get_footprint_from_ctrip()
    # store_all_photos()
    add_activitys()
