from typing import Literal

from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    field_validator,
)


class RegisterRequest(BaseModel):

    email: EmailStr

    password: str = Field(
        min_length=8,
        max_length=128,
    )

    full_name: str = Field(
        default="",
        max_length=120,
    )


class LoginRequest(BaseModel):

    email: EmailStr

    password: str


class HomeRequest(BaseModel):

    budget: float = Field(
        gt=0,
        le=10_000_000,
    )

    rooms: list[str] = Field(
        default_factory=list
    )

    items: dict[str, int] = Field(
        default_factory=dict
    )

    style: str = Field(
        default="modern",
        max_length=80,
    )

    city: str = Field(
        default="Villupuram",
        max_length=100,
    )

    notes: str = Field(
        default="",
        max_length=1000,
    )

    @field_validator("rooms")
    @classmethod
    def clean_rooms(cls, value):

        return [
            str(room).strip()
            for room in value
            if str(room).strip()
        ][:10]


class PartyRequest(BaseModel):

    budget: float = Field(
        gt=0,
        le=10_000_000,
    )

    guests: int = Field(
        gt=0,
        le=10000,
    )

    event_type: str = Field(
        default="birthday",
        max_length=80,
    )

    venue: str = Field(
        default="home",
        max_length=120,
    )

    city: str = Field(
        default="Villupuram",
        max_length=100,
    )

    food_preference: str = Field(
        default="mixed",
        max_length=80,
    )

    notes: str = Field(
        default="",
        max_length=1000,
    )


class RecommendationItem(BaseModel):

    category: str

    name: str

    estimated_price: float = Field(
        ge=0
    )

    quantity: int = Field(
        default=1,
        ge=1,
    )

    platform: str

    reason: str

    search_url: str = ""


class RecommendationResponse(BaseModel):

    planner: Literal[
        "home",
        "party",
        "jewelry",
    ]

    budget: float

    allocated_total: float

    summary: str

    tips: list[str] = Field(
        default_factory=list
    )

    allocations: dict[str, float] = Field(
        default_factory=dict
    )

    recommendations: list[RecommendationItem] = Field(
        default_factory=list
    )

    ai_used: bool = False


class JewelryRequest(BaseModel):

    budget: float = Field(
        gt=0,
        le=10_000_000,
    )

    occasion: str = Field(
        default="party",
        max_length=100,
    )

    style: str = Field(
        default="minimal",
        max_length=100,
    )

    outfit_description: str = Field(
        default="",
        max_length=1000,
    )

    preferred_metal: str = Field(
        default="any",
        max_length=80,
    )

    city: str = Field(
        default="Villupuram",
        max_length=100,
    )

    notes: str = Field(
        default="",
        max_length=1000,
    )