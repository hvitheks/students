from sqlalchemy import create_engine, Column, Integer, String, Date, ForeignKey, Table
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from sqlalchemy.dialects.postgresql import ARRAY

URL = 'postgresql://secUREusER:StrongEnoughPassword)@51.250.26.59:5432/query'

engine = create_engine(URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class RetakeSubjectDB(Base):
    __tablename__ = 'retake_subjects'

    id = Column(Integer, primary_key=True, index=True)
    subject_name = Column(String, nullable=False)
    retake_date = Column(Date, nullable=False)
    total_seats = Column(Integer, nullable=False)
    remaining_seats = Column(Integer, nullable=False)

class StudentDB(Base):
    __tablename__ = 'students'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    login = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    retakes = Column(ARRAY(Integer), default=[])

Base.metadata.create_all(bind=engine)
