from robyn import SubRouter, jsonify

from models import *
import utils

apiRouter = SubRouter(__file__, prefix="/api")


@apiRouter.post("/new_visitor")
async def new_visitor(request):
    session = Session()
    data = request.json()
    # 访客数量操作
    fingerprint = data.get("fingerprint")
    if fingerprint:
        exist_fingerprint = (
            session.query(Fingerprint)
            .filter(Fingerprint.fingerprint == fingerprint)
            .first()
        )
        if not exist_fingerprint:
            new_fingerprint = Fingerprint(fingerprint=fingerprint)
            session.add(new_fingerprint)
            charlie = session.query(Charlie).first()
            charlie.visitorNumber += 1
            session.commit()
    session.close()
    return jsonify(
        {
            "status": 200,
            "message": "success",
        }
    )


@apiRouter.post("/login")
async def login(request):
    session = Session()
    data = request.json()
    username = data.get("username")
    admin = session.query(Admin).filter(Admin.name == username).first()
    if not admin:
        return jsonify({"status": 401, "message": "用户不存在"})
    password = data.get("password")
    if not admin.check_password(password):
        return jsonify({"status": 402, "message": "密码错误"})
    sessionid = utils.generate_sessionid(admin.id)
    session.close()
    return jsonify({"status": 200, "message": "登录成功", "sessionid": sessionid})


@apiRouter.post("/check_sessionid")
async def check_sessionid(request):
    data = request.json()
    sessionid = data.get("sessionid")
    res = utils.check_sessionid(sessionid)
    admin_id = res["user_id"] if res else None
    return jsonify({"status": 200, "message": "success", "admin_id": admin_id})


@apiRouter.post("/get_charlie")
async def get_charlie(request):
    session = Session()
    data = request.json()
    lang = data.get("lang", "Chinese")
    charlie = session.query(Charlie).first()
    session.commit()
    charlie = charlie.to_json() if lang == "Chinese" else charlie.to_json_ENG()
    session.close()
    return jsonify({"status": 200, "message": "success", "charlie": charlie})


@apiRouter.post("/get_talents")
async def get_talents(request):
    session = Session()
    data = request.json()
    lang = data.get("lang", "Chinese")
    talents = session.query(Talent).all()
    talents = [
        talent.to_json() if lang == "Chinese" else talent.to_json_ENG()
        for talent in talents
    ]
    session.close()
    return jsonify({"status": 200, "message": "success", "talents": talents})


@apiRouter.post("/delete_talent")
async def delete_talent(request):
    session = Session()
    headers = request.headers
    cookie = utils.parse_cookie_string(headers.get("cookie"))
    sessionid = cookie.get("sessionid")
    if not cookie or not sessionid or not utils.check_sessionid(sessionid):
        return jsonify(
            {
                "status": 403,
                "message": "No permission",
            }
        )
    data = request.json()
    id = data.get("id")
    talent = session.get(Talent, id)
    if not talent:
        return jsonify(
            {
                "status": 404,
                "message": "Talent not found",
            }
        )
    session.delete(talent)
    session.commit()
    session.close()
    return jsonify(
        {
            "status": 200,
            "message": "success",
        }
    )


@apiRouter.post("/get_achievements")
async def get_achievements(request):
    session = Session()
    data = request.json()
    lang = data.get("lang", "Chinese")
    achievements = session.query(Achievement).all()
    achievements = [
        achievement.to_json() if lang == "Chinese" else achievement.to_json_ENG()
        for achievement in achievements
    ]
    session.close()
    return jsonify({"status": 200, "message": "success", "achievements": achievements})


@apiRouter.post("/delete_achievement")
async def delete_achievement(request):
    session = Session()
    headers = request.headers
    cookie = utils.parse_cookie_string(headers.get("cookie"))
    sessionid = cookie.get("sessionid")
    if not cookie or not sessionid or not utils.check_sessionid(sessionid):
        return jsonify(
            {
                "status": 403,
                "message": "No permission",
            }
        )
    data = request.json()
    id = data.get("id")
    achievement = session.get(Achievement, id)
    if not achievement:
        return jsonify(
            {
                "status": 404,
                "message": "Achievement not found",
            }
        )
    session.delete(achievement)
    session.commit()
    session.close()
    return jsonify(
        {
            "status": 200,
            "message": "success",
        }
    )


@apiRouter.post("/get_growthTimeline")
async def get_growthTimeline(request):
    session = Session()
    data = request.json()
    lang = data.get("lang", "Chinese")
    growthTimelines = session.query(GrowthTimeline).all()
    growthTimelines = [
        growthTimeline.to_json() if lang == "Chinese" else growthTimeline.to_json_ENG()
        for growthTimeline in growthTimelines
    ]
    session.close()
    return jsonify(
        {"status": 200, "message": "success", "growthTimelines": growthTimelines}
    )


@apiRouter.post("/delete_growthTimeline")
async def delete_growthTimeline(request):
    session = Session()
    headers = request.headers
    cookie = utils.parse_cookie_string(headers.get("cookie"))
    sessionid = cookie.get("sessionid")
    if not cookie or not sessionid or not utils.check_sessionid(sessionid):
        return jsonify(
            {
                "status": 403,
                "message": "No permission",
            }
        )
    data = request.json()
    id = data.get("id")
    growthTimeline = session.get(GrowthTimeline, id)
    if not growthTimeline:
        return jsonify(
            {
                "status": 404,
                "message": "GrowthTimeline not found",
            }
        )
    session.delete(growthTimeline)
    session.commit()
    session.close()
    return jsonify(
        {
            "status": 200,
            "message": "success",
        }
    )


@apiRouter.post("/get_bubbles")
async def get_bubbles(request):
    session = Session()
    data = request.json()
    lang = data.get("lang", "Chinese")
    bubbles = session.query(Bubble).all()
    bubbles = [
        bubble.to_json() if lang == "Chinese" else bubble.to_json_ENG()
        for bubble in bubbles
    ]
    session.close()
    return jsonify({"status": 200, "message": "success", "bubbles": bubbles})


@apiRouter.post("/delete_bubble")
async def delete_bubble(request):
    session = Session()
    headers = request.headers
    cookie = utils.parse_cookie_string(headers.get("cookie"))
    sessionid = cookie.get("sessionid")
    if not cookie or not sessionid or not utils.check_sessionid(sessionid):
        return jsonify(
            {
                "status": 403,
                "message": "No permission",
            }
        )
    data = request.json()
    id = data.get("id")
    bubble = session.get(Bubble, id)
    if not bubble:
        return jsonify(
            {
                "status": 404,
                "message": "Bubble not found",
            }
        )
    session.delete(bubble)
    session.commit()
    session.close()
    return jsonify(
        {
            "status": 200,
            "message": "success",
        }
    )


@apiRouter.post("/travel/getPlacesBeenTo")
async def getPlacesBeenTo(request):
    session = Session()
    data = request.json()
    lang = data.get("lang", "Chinese")
    places = session.query(PlaceBeenTo).order_by(PlaceBeenTo.dateStart.desc()).all()
    places = [
        place.to_json() if lang == "Chinese" else place.to_json_ENG()
        for place in places
    ]
    session.close()
    return jsonify({"status": 200, "message": "success", "places": places})


@apiRouter.post("/travel/getTravelPhotos")
async def getTravelPhotos(request):
    session = Session()
    data = request.json()
    travelId = data.get("travelId")
    photos = (
        session.query(TravelPhoto)
        .filter(TravelPhoto.travelId == travelId, TravelPhoto.isShown == True)
        .all()
    )
    photos = [photo.to_json() for photo in photos]
    session.close()
    return jsonify({"status": 200, "message": "success", "photos": photos})
