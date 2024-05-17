import os
import uvicorn
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Annotated
from database import database as database
from database.database import RetakeSubjectDB
from model.model import RetakeSubject

app = FastAPI()

database.Base.metadata.create_all(bind=database.engine)


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


@app.get("/health", status_code=status.HTTP_200_OK)
async def service_alive():
    return {'message': 'Service alive'}


@app.post("/add_subject", response_model=RetakeSubject)
async def add_subject(subject: RetakeSubject, db: db_dependency):
    new_subject = RetakeSubjectDB(**subject.dict())
    db.add(new_subject)
    db.commit()
    db.refresh(new_subject)
    return new_subject


@app.get("/subjects", response_model=list[RetakeSubject])
async def list_subjects(db: db_dependency):
    return db.query(RetakeSubjectDB).all()


@app.get("/get_subject_by_id/{subject_id}", response_model=RetakeSubject)
async def get_subject_by_id(subject_id: int, db: db_dependency):
    subject = db.query(RetakeSubjectDB).filter(RetakeSubjectDB.id == subject_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    return subject


@app.delete("/delete_subject/{subject_id}")
async def delete_subject(subject_id: int, db: db_dependency):
    subject = db.query(RetakeSubjectDB).filter(RetakeSubjectDB.id == subject_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    db.delete(subject)
    db.commit()
    return {"message": "Subject deleted successfully"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=80)
