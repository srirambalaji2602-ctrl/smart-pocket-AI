from fastapi import (
    APIRouter,
    Depends,
    Form,
    HTTPException,
    Request,
    Response,
)

from sqlalchemy.orm import Session

from app.models.db_models import User
from ..models.db_models import User
from ..models.schemas import (
    LoginRequest,
    RegisterRequest,
)
from ..services.auth_service import (
    create_access_token,
    hash_password,
    verify_password,
)


router = APIRouter(
    tags=["auth"]
)


def _login_user(
    response: Response,
    user: User,
):

    token = create_access_token(
        user.id,
        user.email,
    )

    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        samesite="lax",
        max_age=60 * 60 * 24,
        secure=False,
    )

    return {
        "message": "Login successful",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
        },
    }


@router.post("/register")
def register(
    payload: RegisterRequest,
    response: Response,
    db: Session = Depends(get_db),
):

    email = payload.email.lower().strip()

    existing_user = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )

    if existing_user:

        raise HTTPException(
            status_code=409,
            detail="Email is already registered",
        )

    user = User(
        email=email,
        full_name=payload.full_name.strip(),
        password_hash=hash_password(
            payload.password
        ),
    )

    db.add(user)

    db.commit()

    db.refresh(user)

    return _login_user(
        response,
        user,
    )


@router.post("/login")
def login(
    payload: LoginRequest,
    response: Response,
    db: Session = Depends(get_db),
):

    email = payload.email.lower().strip()

    user = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )

    if not user or not verify_password(
        payload.password,
        user.password_hash,
    ):

        raise HTTPException(
            status_code=401,
            detail="Invalid email or password",
        )

    return _login_user(
        response,
        user,
    )


@router.post("/token")
def token(
    username: str = Form(...),
    password: str = Form(...),
    response: Response = None,
    db: Session = Depends(get_db),
):

    user = (
        db.query(User)
        .filter(
            User.email == username.lower().strip()
        )
        .first()
    )

    if not user or not verify_password(
        password,
        user.password_hash,
    ):

        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
        )

    access_token = create_access_token(
        user.id,
        user.email,
    )

    if response is not None:

        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            samesite="lax",
            max_age=86400,
        )

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


@router.post("/logout")
def logout(response: Response):

    response.delete_cookie(
        "access_token"
    )

    return {
        "message": "Logged out"
    }


@router.get("/session-info")
def session_info(
    request: Request,
    db: Session = Depends(get_db),
):

    token = request.cookies.get(
        "access_token"
    )

    if not token:

        return {
            "authenticated": False
        }

    try:

        from ..services.auth_service import (
            decode_access_token
        )

        payload = decode_access_token(
            token
        )

        user = db.get(
            User,
            int(payload["sub"])
        )

        if not user:

            return {
                "authenticated": False
            }

        return {
            "authenticated": True,
            "user": {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
            },
        }

    except Exception:

        return {
            "authenticated": False
        }


@router.get("/session-data")
def session_data(
    request: Request,
    db: Session = Depends(get_db),
):

    info = session_info(
        request,
        db,
    )

    if not info["authenticated"]:

        raise HTTPException(
            status_code=401,
            detail="Login required",
        )

    return {
        "user": info["user"],
        "message": (
            "Session data is available "
            "for personalization."
        ),
    }