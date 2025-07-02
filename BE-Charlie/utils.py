import base64
import hashlib
import hmac
import re
import time

from config import LOGIN_SECRET


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
    sessionid = f"userId={user_id}&timestamp={timestamp}&signature={signature}&algorithm=sha256"
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
    pattern = rf"^userId=(\d+)&timestamp=(\d+)&signature=(.+)&algorithm=sha256$"  # 必须用()包含住捕获组才能被match.group捕获
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
