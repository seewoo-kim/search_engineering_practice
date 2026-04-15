import os
from typing import Optional
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import Column, BigInteger, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()
SQLALCHEMY_DATABASE_URL = os.getenv("DB_URL")

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class PressList(Base):
    __tablename__ = "press_list"
    press_list_id = Column(BigInteger, primary_key=True, index=True)
    press_date = Column(String(20))
    press_url = Column(String(2000))
    company_name = Column(String(200))
    press_title = Column(String(2000))

class PressListResponse(BaseModel):
    press_list_id: int
    press_date: Optional[str]
    press_url: Optional[str]
    company_name: Optional[str]
    press_title: Optional[str]

    class Config:
        from_attributes = True

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI()
@app.get("/press/{press_list_id}", response_model = PressListResponse)
def get_press_item(press_list_id: int, db: Session = Depends(get_db)):
    item = db.query(PressList).filter(PressList.press_list_id == press_list_id).first()

    if item is None:
        raise HTTPException(status_code=404, detail="해당 ID의 데이터를 찾을 수 없습니다.")
    
    return item