import json

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..models.db_models import User
from ..dependencies import get_current_user
from ..models.db_models import (
    RecommendationHistory,
    User,
)


router = APIRouter(
    tags=["history"]
)


@router.get("/history")
def history(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    rows = (
        db.query(RecommendationHistory)
        .filter(
            RecommendationHistory.user_id
            == user.id
        )
        .order_by(
            RecommendationHistory.created_at.desc()
        )
        .limit(50)
        .all()
    )

    return [
        {
            "id": row.id,
            "planner_type": row.planner_type,
            "request": json.loads(
                row.request_json
            ),
            "response": json.loads(
                row.response_json
            ),
            "created_at": (
                row.created_at.isoformat()
                if row.created_at
                else None
            ),
        }
        for row in rows
    ]