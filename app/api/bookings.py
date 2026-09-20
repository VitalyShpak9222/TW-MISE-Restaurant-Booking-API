from datetime import date
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_session
from app.schemas.booking import BookingCreate, BookingOut
from app.services.booking_service import BookingService

router = APIRouter(prefix="/bookings", tags=["bookings"])

@router.post("", response_model=BookingOut, status_code=status.HTTP_201_CREATED)
async def create_booking(
    payload: BookingCreate,
    session: AsyncSession = Depends(get_session),
) -> BookingOut:
    return await BookingService.create_booking(session=session, payload=payload)

@router.get("", response_model=list[BookingOut])
async def list_bookings(
    booking_date: date | None = Query(default=None, alias="date"),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
) -> list[BookingOut]:
    return await BookingService.list_bookings(
        session=session,
        booking_date=booking_date,
        offset=offset,
        limit=limit,
    )

@router.get("/{booking_id}", response_model=BookingOut)
async def get_booking(
    booking_id: int,
    session: AsyncSession = Depends(get_session),
) -> BookingOut:
    return await BookingService.get_booking(session=session, booking_id=booking_id)

@router.delete("/{booking_id}", response_model=BookingOut)
async def cancel_booking(
    booking_id: int,
    session: AsyncSession = Depends(get_session),
) -> BookingOut:
    return await BookingService.cancel_booking(session=session, booking_id=booking_id)