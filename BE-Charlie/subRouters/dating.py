from robyn import SubRouter, jsonify
from dateutil import parser

from models import *
import utils

datingRouter = SubRouter(__file__, prefix="/dating")


@datingRouter.post("/get_activity_length")
async def get_activity_length():
    with Session() as session:
        activity_length = session.query(Activity).count()
        return jsonify({
            "status": 200,
            "message": "success",
            "activity_length": activity_length
        })


@datingRouter.post("/get_all_activities")
async def get_all_activities(request):
    with Session() as session:
        data = request.json()
        lang = data.get("lang", "Chinese")
        activities = session.query(Activity).order_by(
            Activity.date.desc(),
        ).all()
        return jsonify({
            "status": 200,
            "message": "success",
            "activities": [activity.to_json() if lang == "Chinese" else activity.to_json_ENG() for activity in activities]
        })


@datingRouter.post("/unlock_activity")
async def unlock_activity(request):
    headers = request.headers
    cookie = utils.parse_cookie_string(headers.get("cookie"))
    sessionid = cookie.get("sessionid")
    if not cookie or not sessionid or not utils.check_sessionid(sessionid):
        return jsonify({
            "status": 403,
            "message": "No permission",
        })

    with Session() as session:
        # multipart/form-data 下，用 form_data 获取文本字段
        form = request.form_data
        activity_id = form.get("activity_id")
        date = form.get("date")
        description = form.get("description")
        description_ENG = form.get("description_ENG")

        activity = session.get(Activity, activity_id)
        if not activity:
            return jsonify({
                "status": 404,
                "message": "Activity not found",
            })
       
        activity.date = parser.parse(date)
        activity.description = description
        activity.description_ENG = description_ENG

        files = request.files
        if files:
            # 键为文件名，值为文件二进制数据
            # 直接使用 next() 获取第一个键值对
            image_name, image_binary = next(iter(files.items()))
            image_url = utils.upload_file_to_OSS(image_name, image_binary, "images/activities")
            # 注意：Activity模型中的字段名是 imageUrl，不是 image_url
            activity.imageUrl = image_url
        session.commit()

        return jsonify({
            "status": 200,
            "message": "解锁成功",
        })


@datingRouter.post("/delete_activity")
async def delete_activity(request):
    headers = request.headers
    cookie = utils.parse_cookie_string(headers.get("cookie"))
    sessionid = cookie.get("sessionid")
    if not cookie or not sessionid or not utils.check_sessionid(sessionid):
        return jsonify({
            "status": 403,
            "message": "No permission",
        })

    with Session() as session:
        data = request.json()
        activity_id = data.get("activity_id")
        activity = session.get(Activity, activity_id)
        if not activity:
            return jsonify({
                "status": 404,
                "message": "Activity not found",
            })
        session.delete(activity)
        session.commit()
        return jsonify({
            "status": 200,
            "message": "删除成功",
        })