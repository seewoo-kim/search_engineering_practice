from fastapi import FastAPI, HTTPException, Depends, Path
from sqlalchemy.orm import Session

from database import get_db
from models import PressList
from schemas import PressListResponse
from dependencies import verify_api_key, check_rate_limit
from opensearch_client import client
from config import settings

app = FastAPI(
    title="Secure Press API",
    description="인증 및 속도 제한이 적용된 통합 API입니다.",
    dependencies=[Depends(check_rate_limit)]
)

@app.get("/greeting", summary="기본 인사말")
def read_root():
    return {"message" : "Hello world"}

@app.get("/db/press/{press_list_id}", 
         response_model=PressListResponse, 
         summary="DB에서 특정 기사 조회",
         dependencies=[Depends(verify_api_key)])
def get_press_item_db(press_list_id: int, db: Session = Depends(get_db)):
    item = db.query(PressList).filter(PressList.press_list_id == press_list_id).first()
    if item is None:
        raise HTTPException(status_code=404, detail="Data not found in DB")
    return item

@app.get("/search/press/{pressId}", 
         summary="OpenSearch에서 특정 기사 조회",
         dependencies=[Depends(verify_api_key)])
async def get_press_info_search(
    pressId: str = Path(..., description="조회할 기사의 고유 ID")
):
    query = {"query": {"term": {"pressId": pressId}}, "size": 1}
    try:
        response = await client.search(body=query, index=settings.OPENSEARCH_INDEX)
        hits = response['hits']['hits']
        if not hits:
            raise HTTPException(status_code=404, detail="Data not found in OpenSearch")
        return hits[0]['_source']
    except Exception as e:
        if isinstance(e, HTTPException): raise e
        raise HTTPException(status_code=500, detail="Internal Server Error")
