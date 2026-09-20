from datetime import date, time
from pydantic import BaseModel, Field, field_validator
import re

class BookingCreate(BaseModel):
    name: str = Field(min_length=2)
    phone: str
    booking_date: date
    booking_time: time
    guests: int = Field(ge=1, le=12)

    def validate_phone(value: str) -> str:     
        digits = re.sub(r'\D', '', value)
        if len(digits) == 11 and digits[0] in ('7', '8'):
            return value
        raise ValueError(
            'Введите корректный номер: +7 или 8, 10 цифр'
            )
        
class BookingOut(BookingCreate):
    id: int
    status: str  # 'active' | 'cancelled'