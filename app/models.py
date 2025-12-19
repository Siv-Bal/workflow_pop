from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime

from app.database import Base


class Workflow(Base):
    __tablename__ = "workflows"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=False)
    platform = Column(String, nullable=False)
    country = Column(String, nullable=False)

    views = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    comments = Column(Integer, default=0)

    replies = Column(Integer, nullable=True)
    contributors = Column(Integer, nullable=True)

    like_to_view_ratio = Column(Float, default=0.0)
    comment_to_view_ratio = Column(Float, default=0.0)

    popularity_score = Column(Integer)
    engagement_score = Column(Integer)
    volume_score = Column(Integer)
    trend_score = Column(Integer)
    trend_direction = Column(String, nullable=True)
    trend_avg_interest = Column(Float, nullable=True)


    explanation = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
