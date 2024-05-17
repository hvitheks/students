from pydantic import BaseModel
from datetime import date
from typing import List, Optional

class RetakeSubject(BaseModel):
    id: Optional[int]
    subject_name: str
    retake_date: date
    total_seats: int
    remaining_seats: int

class Student(BaseModel):
    id: Optional[int]
    name: str
    login: str
    password: str
    retakes: List[int] = []
