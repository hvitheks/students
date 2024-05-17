import os
import uvicorn
from fastapi import FastAPI, Depends, HTTPException, status, Form, Header
from sqlalchemy.orm import Session
from typing import Annotated
from database import database as database
from database.database import RetakeSubjectDB
from model.model import RetakeSubject
from keycloak import KeycloakOpenID

app = FastAPI()

database.Base.metadata.create_all(bind=database.engine)


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]

KEYCLOAK_URL = "http://keycloak:8080/"
KEYCLOAK_CLIENT_ID = "testClient"
KEYCLOAK_REALM = "testRealm"
KEYCLOAK_CLIENT_SECRET = "**********"

keycloak_openid = KeycloakOpenID(server_url=KEYCLOAK_URL,
                                 client_id=KEYCLOAK_CLIENT_ID,
                                 realm_name=KEYCLOAK_REALM,
                                 client_secret_key=KEYCLOAK_CLIENT_SECRET)


@app.post("/sign_in")
async def sign_in(username: str = Form(...), password: str = Form(...)):
    try:
        token = keycloak_openid.token(grant_type=["password"],
                                      username=username,
                                      password=password)
        return token
    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail="Не удалось получить токен")


def check_for_role(token):
    try:
        token_info = keycloak_openid.introspect(token)
        if "test" not in token_info["realm_access"]["roles"]:
            raise HTTPException(status_code=403, detail="Access denied")
        return token_info
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token or access denied")


@app.get("/health", status_code=status.HTTP_200_OK)
async def service_alive(token: str = Header()):
    if (check_for_role(token)):
        return {'message': 'service alive'}
    else:
        return "Wrong JWT Token"


@app.post("/add_subject", response_model=RetakeSubject)
async def add_subject(subject: RetakeSubject, db: db_dependency, token: str = Header()):
    if (check_for_role(token)):
        new_subject = RetakeSubjectDB(**subject.dict())
        db.add(new_subject)
        db.commit()
        db.refresh(new_subject)
        return new_subject
    else:
        return "Wrong JWT Token"


@app.get("/subjects", response_model=list[RetakeSubject])
async def list_subjects(db: db_dependency, token: str = Header()):
    if (check_for_role(token)):
        return db.query(RetakeSubjectDB).all()
    else:
        return "Wrong JWT Token"


@app.get("/get_subject_by_id/{subject_id}", response_model=RetakeSubject)
async def get_subject_by_id(subject_id: int, db: db_dependency, token: str = Header()):
    if (check_for_role(token)):
        subject = db.query(RetakeSubjectDB).filter(RetakeSubjectDB.id == subject_id).first()
        if not subject:
            raise HTTPException(status_code=404, detail="Subject not found")
        return subject
    else:
        return "Wrong JWT Token"


@app.delete("/delete_subject/{subject_id}")
async def delete_subject(subject_id: int, db: db_dependency, token: str = Header()):
    if (check_for_role(token)):
        subject = db.query(RetakeSubjectDB).filter(RetakeSubjectDB.id == subject_id).first()
        if not subject:
            raise HTTPException(status_code=404, detail="Subject not found")
        db.delete(subject)
        db.commit()
        return {"message": "Subject deleted successfully"}
    else:
        return "Wrong JWT Token"


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=80)
