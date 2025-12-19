from pydantic import BaseModel, field_validator
from typing import Optional


class WorkflowOut(BaseModel):
    name: str
    platform: str
    country: str

    views: Optional[int] = 0
    likes: Optional[int] = 0
    comments: Optional[int] = 0

    like_to_view_ratio: Optional[float] = 0.0
    comment_to_view_ratio: Optional[float] = 0.0

    popularity_score: int
    engagement_score: int
    volume_score: int
    trend_score: int
    trend_direction:Optional[str]
    trend_avg_interest:Optional[float]

    explanation: str

    # 🔥 THIS IS THE KEY PART 🔥
    @field_validator(
        "views",
        "likes",
        "comments",
        mode="before"
    )
    @classmethod
    def none_to_zero_int(cls, v):
        return v if v is not None else 0

    @field_validator(
        "like_to_view_ratio",
        "comment_to_view_ratio",
        mode="before"
    )
    @classmethod
    def none_to_zero_float(cls, v):
        return v if v is not None else 0.0

    class Config:
        from_attributes = True
