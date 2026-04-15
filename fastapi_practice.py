import os
from typing import Optional
from fastapi import FastAPI, HTTPException, Depends, Path
from sqlalchemy import Column, BigInteger, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv
from pydantic import BaseModel
from opensearchpy import OpenSearch

# 1. 환경 변수 로드
load_dotenv()

# 2. 데이터베이스 설정 (press_list_api.py)
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

# 3. OpenSearch 설정 (opensearch_api.py)
host = os.getenv("OPENSEARCH_HOST") 
port = 443
auth = (os.getenv("OPENSEARCH_ID"), os.getenv("OPENSEARCH_PW"))

client = OpenSearch(
    hosts=[{'host': host, 'port': port, 'scheme': 'https'}],
    http_compress=True,
    http_auth=auth,
    use_ssl=True,
    ssl_show_warn=False
)

INDEX_NAME = "press-list-alias"

# 4. FastAPI 앱 초기화
app = FastAPI(
    title="Integrated Press API",
    description="hello_world, press_list_api, opensearch_api 기능이 통합된 API입니다."
)

# 5. 엔드포인트 정의

# hello_world.py 에서 가져옴
@app.get("/greeting", summary="기본 인사말")
def read_root():
    return {"message" : "Hello world"}

# press_list_api.py 에서 가져옴 (DB 조회)
@app.get("/db/press/{press_list_id}", response_model=PressListResponse, summary="DB에서 특정 기사 조회")
def get_press_item_db(press_list_id: int, db: Session = Depends(get_db)):
    item = db.query(PressList).filter(PressList.press_list_id == press_list_id).first()

    if item is None:
        raise HTTPException(status_code=404, detail="해당 ID의 데이터를 DB에서 찾을 수 없습니다.")
    
    return item

# opensearch_api.py 에서 가져옴 (OpenSearch 조회)
@app.get("/search/press/{pressId}", summary="OpenSearch에서 특정 기사 조회")
async def get_press_info_search(
    pressId: str = Path(..., description="조회할 기사의 고유 ID")
):
    query = {
        "query": {
            "term": {
                "pressId": pressId
            }
        },
        "size": 1
    }

    try:
        response = client.search(
            body=query,
            index=INDEX_NAME
        )

        hits = response['hits']['hits']

        if not hits:
            raise HTTPException(status_code=404, detail=f"Press ID '{pressId}'를 OpenSearch에서 찾을 수 없습니다.")
        
        return hits[0]['_source']
    
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"서버 내부 오류: {str(e)}")
