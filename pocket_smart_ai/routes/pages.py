from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates


router = APIRouter()


templates = Jinja2Templates(
    directory=str(
        Path(__file__).resolve().parent.parent / "templates"
    )
)


@router.get(
    "/",
    response_class=HTMLResponse,
)
def home(request: Request):

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request
        },
    )


@router.get(
    "/login",
    response_class=HTMLResponse,
)
def login_page(request: Request):

    return templates.TemplateResponse(
        "login.html",
        {
            "request": request
        },
    )


@router.get(
    "/register",
    response_class=HTMLResponse,
)
def register_page(request: Request):

    return templates.TemplateResponse(
        "register.html",
        {
            "request": request
        },
    )


@router.get(
    "/dashboard",
    response_class=HTMLResponse,
)
def dashboard_page(request: Request):

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request
        },
    )


@router.get(
    "/home-planner",
    response_class=HTMLResponse,
)
def home_planner(request: Request):

    return templates.TemplateResponse(
        "home_planner.html",
        {
            "request": request
        },
    )


@router.get(
    "/party-planner",
    response_class=HTMLResponse,
)
def party_planner(request: Request):

    return templates.TemplateResponse(
        "party_planner.html",
        {
            "request": request
        },
    )


@router.get(
    "/jewelry-planner",
    response_class=HTMLResponse,
)
def jewelry_planner(request: Request):

    return templates.TemplateResponse(
        "jewelry_planner.html",
        {
            "request": request
        },
    )


@router.get(
    "/history",
    response_class=HTMLResponse,
)
def history_page(request: Request):

    return templates.TemplateResponse(
        "history.html",
        {
            "request": request
        },
    )