from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.booking import Booking, BookingStatus
from app.schemas.booking import BookingCreate
from datetime import date

class BookingService:
    @staticmethod
    async def create_booking(session: AsyncSession, payload: BookingCreate) -> Booking:
        conflict_query = select(Booking).where(
            Booking.booking_date == payload.booking_date,
            Booking.booking_time == payload.booking_time,
            Booking.status == BookingStatus.active,
        )
        conflict = await session.scalar(conflict_query)
        if conflict is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Booking slot is already taken",
            )

        booking = Booking(
            name=payload.name,
            phone=payload.phone,
            booking_date=payload.booking_date,
            booking_time=payload.booking_time,
            guests=payload.guests,
            status=BookingStatus.active,
        )
        session.add(booking)
        await session.commit()
        await session.refresh(booking)
        return booking

    @staticmethod
    async def list_bookings(
        session: AsyncSession,
        booking_date: date | None = None,
        offset: int = 0,
        limit: int = 100,
    ) -> list[Booking]:
        query = select(Booking).order_by(Booking.booking_date, Booking.booking_time)
        if booking_date is not None:
            query = query.where(Booking.booking_date == booking_date)
        result = await session.scalars(query.offset(offset).limit(limit))
        return list(result)

    @staticmethod
    async def get_booking(session: AsyncSession, booking_id: int) -> Booking:
        booking = await session.get(Booking, booking_id)
        if booking is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found",
            )
        return booking

    @staticmethod
    async def cancel_booking(session: AsyncSession, booking_id: int) -> Booking:
        booking = await BookingService.get_booking(session=session, booking_id=booking_id)
        booking.status = BookingStatus.cancelled
        await session.commit()
        await session.refresh(booking)
        return booking