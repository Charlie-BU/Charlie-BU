import json
from robyn import SubRouter, jsonify
from sqlalchemy import case

from models import *
from AI import get_ark_summary
import utils

datingRouter = SubRouter(__file__, prefix="/dating")


@datingRouter.post("/getAllActivities")
async def getAllActivities(request):
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

