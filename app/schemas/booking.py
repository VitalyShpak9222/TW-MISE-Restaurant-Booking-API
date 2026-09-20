import re
from datetime import date, time, timedelta
from pydantic import BaseModel, Field, field_validator, ConfigDict

NAME_PATTERN = re.compile(r"^[^\W\d_]+(?:[ -][^\W\d_]+)*$", re.UNICODE)
PHONE_PATTERN = re.compile(r"^(?:\+7|8)\d{10}$")
ALLOWED_HOURS = set(range(12, 23))

class BookingCreate(BaseModel):
    name: str = Field(min_length=2)
    phone: str
    booking_date: date
    booking_time: time
    guests: int = Field(ge=1, le=12)

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        normalized = " ".join(value.strip().split())
        if len(normalized) < 2 or not NAME_PATTERN.fullmatch(normalized):
            raise ValueError("Name must contain only letters, spaces and hyphens")
        return normalized

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, value: str) -> str:     
        digits = re.sub(r'\D', '', value)
        if not PHONE_PATTERN.fullmatch(value):
            raise ValueError(
                'Введите корректный номер: +7 или 8, 10 цифр'
            )
        
        return value

    @field_validator("booking_date")
    @classmethod
    def validate_booking_date(cls, value: date) -> date:
        today = date.today()
        max_date = today + timedelta(days=90)
        if value < today:
            raise ValueError("Booking date cannot be earlier than today")
        if value > max_date:
            raise ValueError("Booking date cannot be later than 90 days from today")
        return value

    @field_validator("booking_time")
    @classmethod
    def validate_booking_time(cls, value: time) -> time:
        if (
            value.hour not in ALLOWED_HOURS
            or value.minute != 0
            or value.second != 0
            or value.microsecond != 0
        ):
            raise ValueError("Booking time must be an hourly slot from 12:00 to 22:00")
        return value

class BookingOut(BookingCreate):
    id: int
    status: str  # 'active' | 'cancelled'

    model_config = ConfigDict(from_attributes=True)