from sqlalchemy import Column, Integer, String

from db.database import Base


class UserSettings(Base):
    __tablename__ = "user_settings"

    id = Column(Integer, primary_key=True, index=True)
    phrase = Column(String, default="Hello")
    interval = Column(Integer, default=5)
