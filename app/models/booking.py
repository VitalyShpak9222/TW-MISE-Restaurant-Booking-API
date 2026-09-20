from datetime import date, datetime, time
from enum import StrEnum
from sqlalchemy import Date, DateTime, Enum, Integer, String, Time, func
from sqlalchemy.orm import Mapped, mapped_column
from app.db import Base

class BookingStatus(StrEnum):
    active = "active"
    cancelled = "cancelled"

class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    phone: Mapped[str] = mapped_column(String(32), nullable=False)
    booking_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    booking_time: Mapped[time] = mapped_column(Time, nullable=False)
    guests: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[BookingStatus] = mapped_column(
        Enum(BookingStatus),
        nullable=False,
        default=BookingStatus.active,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )