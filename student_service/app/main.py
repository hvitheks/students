import os
import uvicorn
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from typing import Optional
from pydantic import BaseModel

from student_database.database import RetakeSubjectDB, StudentDB, SessionLocal

app = FastAPI()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Модели данных
class StudentCreate(BaseModel):
    name: str
    login: str
    password: str


class StudentLogin(BaseModel):
    login: str
    password: str


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
current_student_id: Optional[int] = None


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/health", status_code=status.HTTP_200_OK)
async def service_alive():
    return {"message": "Service alive"}


@app.post("/register")
async def register_student(student: StudentCreate, db: Session = Depends(get_db)):
    hashed_password = pwd_context.hash(student.password)
    new_student = StudentDB(
        name=student.name,
        login=student.login,
        password=hashed_password
    )
    db.add(new_student)
    db.commit()
    db.refresh(new_student)
    return new_student


@app.post("/login")
async def login_student(student: StudentLogin, db: Session = Depends(get_db)):
    global current_student_id
    db_student = db.query(StudentDB).filter(StudentDB.login == student.login).first()
    if not db_student or not pwd_context.verify(student.password, db_student.password):
        raise HTTPException(status_code=400, detail="Invalid login or password")
    current_student_id = db_student.id
    return {"id": db_student.id, "name": db_student.name}


@app.get("/current_student")
async def current_student(db: Session = Depends(get_db)):
    if current_student_id is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    student = db.query(StudentDB).filter(StudentDB.id == current_student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return {"id": student.id, "name": student.name}


@app.post("/enroll")
async def enroll_student(subject_id: int, db: Session = Depends(get_db)):
    if current_student_id is None:
        raise HTTPException(status_code=401, detail="Not authenticated")

    subject = db.query(RetakeSubjectDB).filter(RetakeSubjectDB.id == subject_id).first()

    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    if subject.remaining_seats < 1:
        raise HTTPException(status_code=400, detail="No remaining seats")

    subject.remaining_seats -= 1
    db.commit()

    student = db.query(StudentDB).filter(StudentDB.id == current_student_id).first()
    student.retakes.append(subject_id)
    db.commit()

    return {"message": "Successfully enrolled"}



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv('PORT', 80)))
