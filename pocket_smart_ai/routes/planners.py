import json

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
)

from sqlalchemy.orm import Session

from app.config import get_settings
from ..models.db_models import User
from app.dependencies import get_current_user
from ..models.db_models import (
    RecommendationHistory,
    User,
)
from ..models.schemas import (
    HomeRequest,
    JewelryRequest,
    PartyRequest,
    RecommendationResponse,
)
from ..services.gemini_service import gemini_service


router = APIRouter(
    tags=["planners"]
)


settings = get_settings()


ALLOWED_IMAGES = {
    "image/jpeg",
    "image/png",
    "image/webp",
}


def save_history(
    db: Session,
    user: User,
    planner: str,
    request_data: dict,
    response_data: dict,
):

    row = RecommendationHistory(
        user_id=user.id,
        planner_type=planner,
        request_json=json.dumps(
            request_data,
            ensure_ascii=False,
        ),
        response_json=json.dumps(
            response_data,
            ensure_ascii=False,
        ),
    )

    db.add(row)

    db.commit()


@router.post(
    "/generate-home",
    response_model=RecommendationResponse,
)
def generate_home(
    payload: HomeRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    result = gemini_service.generate(
        "home",
        payload.model_dump(),
    )

    save_history(
        db,
        user,
        "home",
        payload.model_dump(),
        result,
    )

    return result


@router.post(
    "/generate-party",
    response_model=RecommendationResponse,
)
def generate_party(
    payload: PartyRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    result = gemini_service.generate(
        "party",
        payload.model_dump(),
    )

    save_history(
        db,
        user,
        "party",
        payload.model_dump(),
        result,
    )

    return result


@router.post(
    "/generate-jewelry",
    response_model=RecommendationResponse,
)
async def generate_jewelry(
    budget: float = Form(...),
    occasion: str = Form("party"),
    style: str = Form("minimal"),
    outfit_description: str = Form(""),
    preferred_metal: str = Form("any"),
    city: str = Form("Villupuram"),
    notes: str = Form(""),
    outfit_image: UploadFile | None = File(None),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    payload = JewelryRequest(
        budget=budget,
        occasion=occasion,
        style=style,
        outfit_description=outfit_description,
        preferred_metal=preferred_metal,
        city=city,
        notes=notes,
    )

    image_bytes = None
    mime_type = None

    if outfit_image and outfit_image.filename:

        if outfit_image.content_type not in ALLOWED_IMAGES:

            raise HTTPException(
                status_code=400,
                detail=(
                    "Only JPG, PNG and WEBP "
                    "images are allowed"
                ),
            )

        image_bytes = await outfit_image.read()

        if len(image_bytes) > (
            settings.max_image_mb
            * 1024
            * 1024
        ):

            raise HTTPException(
                status_code=400,
                detail=(
                    f"Image must be <= "
                    f"{settings.max_image_mb} MB"
                ),
            )

        mime_type = outfit_image.content_type

    result = gemini_service.generate(
        "jewelry",
        payload.model_dump(),
        image_bytes,
        mime_type,
    )

    save_history(
        db,
        user,
        "jewelry",
        payload.model_dump(),
        result,
    )

    return result


@router.post(
    "/recommendations-details",
    response_model=RecommendationResponse,
)
def recommendations_details(
    payload: dict,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    planner = payload.get("planner")

    if planner not in {
        "home",
        "party",
        "jewelry",
    }:

        raise HTTPException(
            status_code=400,
            detail=(
                "planner must be home, party "
                "or jewelry"
            ),
        )

    result = gemini_service.generate(
        planner,
        payload,
    )

    save_history(
        db,
        user,
        planner,
        payload,
        result,
    )

    return result