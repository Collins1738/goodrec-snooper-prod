import uuid
from datetime import datetime
from sqlalchemy import String, Boolean, ForeignKey, DateTime, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    phone: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    verified: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=text("NOW()"))

    preferences: Mapped[list["UserPreference"]] = relationship("UserPreference", back_populates="user", cascade="all, delete")
    notified_events: Mapped[list["UserNotifiedEvent"]] = relationship("UserNotifiedEvent", back_populates="user", cascade="all, delete")


class UserPreference(Base):
    __tablename__ = "user_preferences"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"), nullable=False)
    venue_key: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=text("NOW()"))

    user: Mapped["User"] = relationship("User", back_populates="preferences")


class UserNotifiedEvent(Base):
    __tablename__ = "user_notified_events"

    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"), primary_key=True)
    event_id: Mapped[str] = mapped_column(String, primary_key=True)
    notified_at: Mapped[datetime] = mapped_column(DateTime, server_default=text("NOW()"))

    user: Mapped["User"] = relationship("User", back_populates="notified_events")
