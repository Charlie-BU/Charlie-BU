from robyn import SubRouter, jsonify

from models import *
import utils

datingRouter = SubRouter(__file__, prefix="/dating")


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
    # if not cookie or not sessionid or not utils.check_sessionid(sessionid):
    #     return jsonify({
    #         "status": 403,
    #         "message": "No permission",
    #     })
    with Session() as session:
        data = request.json()
        activity_id = data.get("activity_id")
        activity = session.get(Activity, activity_id)
        if not activity:
            return jsonify({
                "status": 404,
                "message": "Activity not found",
            })
        date = data["date"]
        description = data["description"]

        image = request.files
        print(image)
        activity.date = date
        activity.description = description
        session.commit()

        return jsonify({
            "status": 200,
            "message": "解锁成功",
        })
