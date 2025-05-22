from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Integer, Text

from app.db.models.base import Base


class URL(Base):
    __tablename__ = "urls"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(10), unique=True, index=True, nullable=False)
    original_url = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    access_count = Column(Integer, default=0)
