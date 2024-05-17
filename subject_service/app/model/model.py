from pydantic import BaseModel
from typing import Optional
from datetime import date

class RetakeSubject(BaseModel):
    id: Optional[int]
    subject_name: str
    retake_date: date
    total_seats: int
    remaining_seats: int
