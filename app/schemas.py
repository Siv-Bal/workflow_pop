from pydantic import BaseModel
from typing import Optional

class WorkflowResponse(BaseModel):
    workflow: str
    platform: str
    country: str
    popularity_score: int

    engagement_score: int
    volume_score: int
    trend_score: int

    explanation: str

    class Config:
        orm_mode = True


class WorkflowOut(BaseModel):
    name: str
    platform: str
    country: str

    views: int
    likes: int
    comments: int

    like_to_view_ratio: float
    comment_to_view_ratio: float

    popularity_score: int
    engagement_score: int
    volume_score: int
    trend_score: int

    explanation: str

    class Config:
        from_attributes = True
