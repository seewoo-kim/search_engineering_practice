import os
import time
from typing import Optional, List
from fastapi import FastAPI, HTTPException, Depends, Path, Security, Request
from fastapi.security import APIKeyHeader
from sqlalchemy import Column, BigInteger, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv
from pydantic import BaseModel
from opensearchpy import AsyncOpenSearch

# 1. 환경 변수 로드
load_dotenv()

# 2. 인증 설정 (Simple API Key)
API_KEY = os.getenv("APP_API_KEY", None)
api_key_header = APIKeyHeader(name="X-API-KEY", auto_error=True)

async def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Could not validate credentials")
    return api_key

# 3. 간단한 Rate Limiting (In-Memory)
# {ip: [timestamps]}
request_history = {}
RATE_LIMIT_WINDOW = 60 # 60초
MAX_REQUESTS = 10      # 60초당 최대 10회

def check_rate_limit(request: Request):
    client_ip = request.client.host
    now = time.time()
    
    # 해당 IP의 요청 기록 가져오기 및 윈도우 밖의 기록 삭제
    if client_ip not in request_history:
        request_history[client_ip] = []
    
    request_history[client_ip] = [t for t in request_history[client_ip] if now - t < RATE_LIMIT_WINDOW]
    
    if len(request_history[client_ip]) >= MAX_REQUESTS:
        raise HTTPException(status_code=429, detail="Too Many Requests. Please try again later.")
    
    request_history[client_ip].append(now)

# 4. 데이터베이스 설정
SQLALCHEMY_DATABASE_URL = os.getenv("DB_URL")
# ... (생략된 기존 DB 설정 유지) ...
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_recycle=3600
)
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

# 5. OpenSearch 설정
host = os.getenv("OPENSEARCH_HOST") 
port = 443
auth = (os.getenv("OPENSEARCH_ID"), os.getenv("OPENSEARCH_PW"))

client = AsyncOpenSearch(
    hosts=[{'host': host, 'port': port, 'scheme': 'https'}],
    http_compress=True,
    http_auth=auth,
    use_ssl=True,
    verify_certs=True,
    ssl_show_warn=False
)

INDEX_NAME = "press-list-alias"

# 6. FastAPI 앱 초기화
app = FastAPI(
    title="Secure Press API",
    description="인증 및 속도 제한이 적용된 통합 API입니다.",
    dependencies=[Depends(check_rate_limit)] # 모든 엔드포인트에 Rate Limit 적용
)

# 7. 엔드포인트 정의

@app.get("/greeting", summary="기본 인사말")
def read_root():
    return {"message" : "Hello world"}

@app.get("/db/press/{press_list_id}", 
         response_model=PressListResponse, 
         summary="DB에서 특정 기사 조회",
         dependencies=[Depends(verify_api_key)]) # 인증 적용
def get_press_item_db(press_list_id: int, db: Session = Depends(get_db)):
    item = db.query(PressList).filter(PressList.press_list_id == press_list_id).first()
    if item is None:
        raise HTTPException(status_code=404, detail="Data not found in DB")
    return item

@app.get("/search/press/{pressId}", 
         summary="OpenSearch에서 특정 기사 조회",
         dependencies=[Depends(verify_api_key)]) # 인증 적용
async def get_press_info_search(
    pressId: str = Path(..., description="조회할 기사의 고유 ID")
):
    query = {"query": {"term": {"pressId": pressId}}, "size": 1}
    try:
        response = await client.search(body=query, index=INDEX_NAME)
        hits = response['hits']['hits']
        if not hits:
            raise HTTPException(status_code=404, detail="Data not found in OpenSearch")
        return hits[0]['_source']
    except Exception as e:
        if isinstance(e, HTTPException): raise e
        raise HTTPException(status_code=500, detail="Internal Server Error")
