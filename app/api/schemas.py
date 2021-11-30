from pydantic import BaseModel, validator
from enum import IntEnum
import datetime


class Slot(IntEnum):
    midnight_to_eight = 1
    eight_to_four = 2
    four_to_midnight = 3


class Worker(BaseModel):
    id: int
    name: str

    @validator('name', pre=True)
    def blank_string(value, field):
        if value == "":
            return None
        return value

    class Config:
        orm_mode = True


class ShiftResponse(BaseModel):
    slot: Slot
    date: datetime.date

    class Config:
        use_enum_values = True

class ShiftCreate(ShiftResponse):
    worker_id: int


class Shift(ShiftCreate):
    id: int

    class Config:
        orm_mode = True
