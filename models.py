from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    password = Column(String(100), nullable=False)  # <-- пароль в открытом виде
    group = Column(String(20), nullable=False, default="user")
    created_at = Column(DateTime, default=datetime.utcnow)

    advertisements = relationship("Advertisement", back_populates="author_user")

class Advertisement(Base):
    __tablename__ = "advertisements"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    price = Column(Float, nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    author_user = relationship("User", back_populates="advertisements")