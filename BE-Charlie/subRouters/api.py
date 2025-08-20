import json
from robyn import SubRouter, jsonify

from models import *
from AI import get_ark_summary
import utils

apiRouter = SubRouter(__file__, prefix="/api")


@apiRouter.post("/new_visitor")
async def new_visitor(request):
    session = Session()
    data = request.json()
    # 访客数量操作
    fingerprint = data.get("fingerprint")
    if fingerprint:
        exist_fingerprint = session.query(Fingerprint).filter(Fingerprint.fingerprint == fingerprint).first()
        if not exist_fingerprint:
            new_fingerprint = Fingerprint(fingerprint=fingerprint)
            session.add(new_fingerprint)
            charlie = session.query(Charlie).first()
            charlie.visitorNumber += 1
            session.commit()
    session.close()
    return jsonify({
        "status": 200,
        "message": "success",
    })


@apiRouter.post("/login")
async def login(request):
    session = Session()
    data = request.json()
    username = data.get("username")
    admin = session.query(Admin).filter(Admin.name == username).first()
    if not admin:
        return jsonify({
            "status": 401,
            "message": "用户不存在"
        })
    password = data.get("password")
    if not admin.check_password(password):
        return jsonify({
            "status": 402,
            "message": "密码错误"
        })
    sessionid = utils.generate_sessionid(admin.id)
    session.close()
    return jsonify({
        "status": 200,
        "message": "登录成功",
        "sessionid": sessionid
    })


@apiRouter.post("/check_sessionid")
async def check_sessionid(request):
    data = request.json()
    sessionid = data.get("sessionid")
    res = utils.check_sessionid(sessionid)
    admin_id = res["user_id"] if res else None
    return jsonify({
        "status": 200,
        "message": "success",
        "admin_id": admin_id
    })


@apiRouter.post("/get_charlie")
async def get_charlie(request):
    session = Session()
    data = request.json()
    lang = data.get("lang", "Chinese")
    charlie = session.query(Charlie).first()
    session.commit()
    charlie = charlie.to_json() if lang == "Chinese" else charlie.to_json_ENG()
    session.close()
    return jsonify({
        "status": 200,
        "message": "success",
        "charlie": charlie
    })


@apiRouter.post("/get_talents")
async def get_talents(request):
    session = Session()
    data = request.json()
    lang = data.get("lang", "Chinese")
    talents = session.query(Talent).all()
    talents = [talent.to_json() if lang == "Chinese" else talent.to_json_ENG() for talent in talents]
    session.close()
    return jsonify({
        "status": 200,
        "message": "success",
        "talents": talents
    })


@apiRouter.post("/delete_talent")
async def delete_talent(request):
    session = Session()
    headers = request.headers
    cookie = utils.parse_cookie_string(headers.get("cookie"))
    sessionid = cookie.get("sessionid")
    if not cookie or not sessionid or not utils.check_sessionid(sessionid):
        return jsonify({
            "status": 403,
            "message": "No permission",
        })
    data = request.json()
    id = data.get("id")
    talent = session.get(Talent, id)
    if not talent:
        return jsonify({
            "status": 404,
            "message": "Talent not found",
        })
    session.delete(talent)
    session.commit()
    session.close()
    return jsonify({
        "status": 200,
        "message": "success",
    })


@apiRouter.post("/get_achievements")
async def get_achievements(request):
    session = Session()
    data = request.json()
    lang = data.get("lang", "Chinese")
    achievements = session.query(Achievement).all()
    achievements = [achievement.to_json() if lang == "Chinese" else achievement.to_json_ENG() for achievement in
                    achievements]
    session.close()
    return jsonify({
        "status": 200,
        "message": "success",
        "achievements": achievements
    })


@apiRouter.post("/delete_achievement")
async def delete_achievement(request):
    session = Session()
    headers = request.headers
    cookie = utils.parse_cookie_string(headers.get("cookie"))
    sessionid = cookie.get("sessionid")
    if not cookie or not sessionid or not utils.check_sessionid(sessionid):
        return jsonify({
            "status": 403,
            "message": "No permission",
        })
    data = request.json()
    id = data.get("id")
    achievement = session.get(Achievement, id)
    if not achievement:
        return jsonify({
            "status": 404,
            "message": "Achievement not found",
        })
    session.delete(achievement)
    session.commit()
    session.close()
    return jsonify({
        "status": 200,
        "message": "success",
    })


@apiRouter.post("/get_growthTimeline")
async def get_growthTimeline(request):
    session = Session()
    data = request.json()
    lang = data.get("lang", "Chinese")
    growthTimelines = session.query(GrowthTimeline).all()
    growthTimelines = [growthTimeline.to_json() if lang == "Chinese" else growthTimeline.to_json_ENG() for
                       growthTimeline in
                       growthTimelines]
    session.close()
    return jsonify({
        "status": 200,
        "message": "success",
        "growthTimelines": growthTimelines
    })


@apiRouter.post("/delete_growthTimeline")
async def delete_growthTimeline(request):
    session = Session()
    headers = request.headers
    cookie = utils.parse_cookie_string(headers.get("cookie"))
    sessionid = cookie.get("sessionid")
    if not cookie or not sessionid or not utils.check_sessionid(sessionid):
        return jsonify({
            "status": 403,
            "message": "No permission",
        })
    data = request.json()
    id = data.get("id")
    growthTimeline = session.get(GrowthTimeline, id)
    if not growthTimeline:
        return jsonify({
            "status": 404,
            "message": "GrowthTimeline not found",
        })
    session.delete(growthTimeline)
    session.commit()
    session.close()
    return jsonify({
        "status": 200,
        "message": "success",
    })


@apiRouter.post("/get_bubbles")
async def get_bubbles(request):
    session = Session()
    data = request.json()
    lang = data.get("lang", "Chinese")
    bubbles = session.query(Bubble).all()
    bubbles = [bubble.to_json() if lang == "Chinese" else bubble.to_json_ENG() for
               bubble in
               bubbles]
    session.close()
    return jsonify({
        "status": 200,
        "message": "success",
        "bubbles": bubbles
    })


@apiRouter.post("/delete_bubble")
async def delete_bubble(request):
    session = Session()
    headers = request.headers
    cookie = utils.parse_cookie_string(headers.get("cookie"))
    sessionid = cookie.get("sessionid")
    if not cookie or not sessionid or not utils.check_sessionid(sessionid):
        return jsonify({
            "status": 403,
            "message": "No permission",
        })
    data = request.json()
    id = data.get("id")
    bubble = session.get(Bubble, id)
    if not bubble:
        return jsonify({
            "status": 404,
            "message": "Bubble not found",
        })
    session.delete(bubble)
    session.commit()
    session.close()
    return jsonify({
        "status": 200,
        "message": "success",
    })


@apiRouter.post("/get_articles")
async def get_articles(request):
    session = Session()
    headers = request.headers
    cookie = utils.parse_cookie_string(headers.get("cookie"))
    sessionid = cookie.get("sessionid")
    if not cookie or not sessionid or not utils.check_sessionid(sessionid):
        query = session.query(Article).filter(Article.isReleased)
    else:
        query = session.query(Article)
    data = request.json()
    lang = data.get("lang", "Chinese")
    articles = query.order_by(Article.timeLastUpdated.desc()).all()
    articles = [{
                    "id": article.id,
                    "title": article.title_ENG,
                    "timeCreated": article.timeCreated,
                    "timeLastUpdated": article.timeLastUpdated,
                    "tags": article.tag_ENG,
                    "type": article.type,
                    "isReleased": article.isReleased,
                } if lang == "English" else {
        "id": article.id,
        "title": article.title,
        "timeCreated": article.timeCreated,
        "timeLastUpdated": article.timeLastUpdated,
        "tags": article.tags,
        "type": article.type,
        "isReleased": article.isReleased,
    }
                for article in articles]
    session.close()
    return jsonify({
        "status": 200,
        "message": "success",
        "articles": articles
    })


@apiRouter.post("/get_article_content")
async def get_article_content(request):
    session = Session()
    headers = request.headers
    cookie = utils.parse_cookie_string(headers.get("cookie"))
    sessionid = cookie.get("sessionid")
    if not cookie or not sessionid or not utils.check_sessionid(sessionid):
        query = session.query(Article).filter(Article.isReleased)
    else:
        query = session.query(Article)
    data = request.json()
    id = data.get("id")
    lang = data.get("lang", "Chinese")

    article = query.filter(Article.id == id).first()
    if not article:
        return jsonify({
            "status": 404,
            "message": "Article not found",
        })
    article = article.to_json() if lang == "Chinese" else article.to_json_ENG()

    session.close()
    return jsonify({
        "status": 200,
        "message": "success",
        "article": article
    })


@apiRouter.post("/change_article_status")
async def change_article_status(request):
    session = Session()
    headers = request.headers
    cookie = utils.parse_cookie_string(headers.get("cookie"))
    sessionid = cookie.get("sessionid")
    if not cookie or not sessionid or not utils.check_sessionid(sessionid):
        return jsonify({
            "status": 403,
            "message": "No permission",
        })
    data = request.json()
    id = data.get("id")
    article = session.get(Article, id)
    if not article:
        return jsonify({
            "status": 404,
            "message": "Article not found",
        })
    article.isReleased = not article.isReleased
    session.commit()
    session.close()
    return jsonify({
        "status": 200,
        "message": "success",
    })


@apiRouter.post("/get_article_detail/")
async def get_article_detail(request):
    session = Session()
    headers = request.headers
    cookie = utils.parse_cookie_string(headers.get("cookie"))
    sessionid = cookie.get("sessionid")
    if not cookie or not sessionid or not utils.check_sessionid(sessionid):
        return jsonify({
            "status": 403,
            "message": "No permission",
        })
    data = request.json()
    id = data.get("id")
    article = session.get(Article, id)
    if not article:
        return jsonify({
            "status": 404,
            "message": "Article not found",
        })
    article = {
        "id": article.id,
        "title": article.title,
        "content": article.content,
        "content_ENG": article.content_ENG,
        "timeCreated": article.timeCreated,
        "timeLastUpdated": article.timeLastUpdated,
        "tags": article.tags,
        "tag_ENG": article.tag_ENG,
        "type": article.type,
        "isReleased": article.isReleased,
    }
    session.close()
    return jsonify({
        "status": 200,
        "message": "success",
        "article": article
    })


@apiRouter.post("/search_article")
async def search_article(request):
    session = Session()
    data = request.json()
    lang = data.get("lang", "Chinese")
    keyword = data.get("keyword")
    if lang == "English":
        articles = session.query(Article).filter(Article.content_ENG.like(f"%{keyword}%")).order_by(Article.timeLastUpdated.desc()).all()
    else:
        articles = session.query(Article).filter(Article.content.like(f"%{keyword}%")).order_by(Article.timeLastUpdated.desc()).all()

    result = []
    for article in articles:
        if lang == "English":
            title = article.title_ENG
            content = article.content_ENG.replace("#", "")
            content = content.replace(">", "")
            content = content.replace("*", "")
        else:
            title = article.title
            content = article.content.replace("#", "")
            content = content.replace(">", "")
            content = content.replace("*", "")
        content_show = ""

        try:
            # 在文章标题中
            startIndex = title.index(keyword)
            endIndex = startIndex + len(keyword)
            title = title[:startIndex] + "<span style='font-weight: bold; color: red;'>" + title[startIndex:endIndex] + "</span>" + title[endIndex:]
        except ValueError:  # 在文章内容中
            if len(keyword) < 2:  # 关键词不足2个不检查文章内容
                continue
            for index, line in enumerate(content.split("\n")):
                if index == 0:  # 跳过文章标题
                    continue
                if keyword in line:
                    try:
                        startIndex = line.index(keyword)
                    except ValueError:
                        continue
                    endIndex = startIndex + len(keyword)
                    content_show = line[:startIndex] + "<span style='font-weight: bold; color: red;'>" + line[startIndex:endIndex] + "</span>" + line[endIndex:]

        result.append({
            "id": article.id,
            "title": title,
            "content_show": content_show,
            "timeCreated": article.timeCreated,
            "timeLastUpdated": article.timeLastUpdated,
            "tags": article.tags,
        })
    session.close()
    return jsonify({
        "status": 200,
        "message": "success",
        "result": result
    })


@apiRouter.post("/add_article")
async def add_article(request):
    session = Session()
    headers = request.headers
    cookie = utils.parse_cookie_string(headers.get("cookie"))
    sessionid = cookie.get("sessionid")
    if not cookie or not sessionid or not utils.check_sessionid(sessionid):
        return jsonify({
            "status": 403,
            "message": "No permission",
        })
    data = request.json()
    type = int(data.get("type"))
    content = data.get("content")
    content_ENG = data.get("content_ENG")
    tags = data.get("tags")
    if tags:
        tags = json.loads(tags)
    tag_ENG = data.get("tag_ENG")
    if tag_ENG:
        tag_ENG = json.loads(tag_ENG)
    article = Article(type=type, content=content, content_ENG=content_ENG, timeCreated=datetime.now(), tags=tags,
                      tag_ENG=tag_ENG,
                      timeLastUpdated=datetime.now())
    isReleased = True if data.get("isReleased") == "true" else False
    article.isReleased = isReleased
    
    if isReleased:
        aiSummary = get_ark_summary("文章内容如下：\n", content)
        article.aiSummary = aiSummary

    session.add(article)
    session.commit()
    session.close()
    return jsonify({
        "status": 200,
        "message": "success",
    })


@apiRouter.post("/update_article")
async def update_article(request):
    session = Session()
    headers = request.headers
    cookie = utils.parse_cookie_string(headers.get("cookie"))
    sessionid = cookie.get("sessionid")
    if not cookie or not sessionid or not utils.check_sessionid(sessionid):
        return jsonify({
            "status": 403,
            "message": "No permission",
        })
    data = request.json()
    id = data.get("id")
    article = session.get(Article, id)
    if not article:
        return jsonify({
            "status": 404,
            "message": "Article not found",
        })
    fields = ["type", "content", "content_ENG", "tags", "tag_ENG"]
    is_updated = False
    for field in fields:
        if getattr(article, field) != data.get(field):
            if field == "type" and getattr(article, field) == int(data.get(field)):
                continue
            if field == "tags":
                if getattr(article, field) != json.loads(data.get(field)):
                    if data.get(field) and data.get(field) != "":
                        article.tags = json.loads(data.get(field))
                        is_updated = True
                        continue
                    else:
                        continue
                else:
                    continue
            if field == "tag_ENG":
                if getattr(article, field) != json.loads(data.get(field)):
                    if data.get(field) and data.get(field) != "":
                        article.tag_ENG = json.loads(data.get(field))
                        is_updated = True
                        continue
                    else:
                        continue
                else:
                    continue
            setattr(article, field, data.get(field))
            is_updated = True
    if not is_updated:
        return jsonify({
            "status": -1,
            "message": "没有更新的内容",
        })
    isReleased = True if data.get("isReleased") == "true" else False
    article.isReleased = isReleased

    if isReleased:
        aiSummary = get_ark_summary("文章内容如下：\n", article.content)
        article.aiSummary = aiSummary

    session.commit()
    session.close()
    return jsonify({
        "status": 200,
        "message": "success",
    })


@apiRouter.post("/regenerate_article_AISummary")
async def regenerate_article_AISummary(request):
    session = Session()
    headers = request.headers
    cookie = utils.parse_cookie_string(headers.get("cookie"))
    sessionid = cookie.get("sessionid")

    data = request.json()
    id = data.get("id")
    article = session.get(Article, id)
    if not article:
        return jsonify({
            "status": 404,
            "message": "Article not found",
        })
    if not article.content:
        return jsonify({
            "status": 400,
            "message": "Article content is empty",
        })

    aiSummary = get_ark_summary("文章内容如下：\n", article.content)
    if not cookie or not sessionid or not utils.check_sessionid(sessionid):
        session.close()
        return jsonify({
            "status": 201,
            "message": "user-success",
            "aiSummary": aiSummary,
        })
    article.aiSummary = aiSummary
    session.commit()
    session.close()
    return jsonify({
        "status": 200,
        "message": "admin-success",
        "aiSummary": aiSummary,
    })


@apiRouter.post("/delete_article")
async def delete_article(request):
    session = Session()
    headers = request.headers
    cookie = utils.parse_cookie_string(headers.get("cookie"))
    sessionid = cookie.get("sessionid")
    if not cookie or not sessionid or not utils.check_sessionid(sessionid):
        return jsonify({
            "status": 403,
            "message": "No permission",
        })
    data = request.json()
    id = data.get("id")
    article = session.get(Article, id)
    if not article:
        return jsonify({
            "status": 404,
            "message": "Article not found",
        })
    session.delete(article)
    session.commit()
    session.close()
    return jsonify({
        "status": 200,
        "message": "success",
    })


@apiRouter.post("/travel/getPlacesBeenTo")
async def getPlacesBeenTo(request):
    session = Session()
    data = request.json()
    lang = data.get("lang", "Chinese")
    places = session.query(PlaceBeenTo).order_by(PlaceBeenTo.dateStart.desc()).all()
    places = [place.to_json() if lang == "Chinese" else place.to_json_ENG() for place in places]
    session.close()
    return jsonify({
        "status": 200,
        "message": "success",
        "places": places
    })


@apiRouter.post("/travel/getTravelPhotos")
async def getTravelPhotos(request):
    session = Session()
    data = request.json()
    travelId = data.get("travelId")
    photos = session.query(TravelPhoto).filter(TravelPhoto.travelId == travelId, TravelPhoto.isShown == True).all()
    photos = [photo.to_json() for photo in photos]
    session.close()
    return jsonify({
        "status": 200,
        "message": "success",
        "photos": photos
    })
