from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health():

    response = client.get(
        "/health"
    )

    assert response.status_code == 200

    assert (
        response.json()["status"]
        == "ok"
    )


def test_pages():

    pages = [

        "/",

        "/login",

        "/register",

        "/dashboard",

        "/home-planner",

        "/party-planner",

        "/jewelry-planner",

        "/history",
    ]

    for path in pages:

        response = client.get(path)

        assert response.status_code == 200


def test_register_login_and_home():

    email = (
        "test_user_"
        + "pocketsmart@example.com"
    )

    password = "Password123!"

    register = client.post(
        "/register",
        json={
            "email": email,
            "password": password,
            "full_name": "Test User",
        },
    )

    assert register.status_code in (
        200,
        409,
    )

    login = client.post(
        "/login",
        json={
            "email": email,
            "password": password,
        },
    )

    assert login.status_code == 200

    home = client.post(
        "/generate-home",
        json={
            "budget": 25000,

            "rooms": [
                "Living Room"
            ],

            "items": {
                "lighting": 2
            },

            "style": "modern",

            "city": "Villupuram",

            "notes": "",
        },
    )

    assert home.status_code == 200

    assert (
        home.json()["planner"]
        == "home"
    )