import os
from fastapi import FastAPI, HTTPException, Path
from opensearchpy import OpenSearch
from dotenv import load_dotenv

load_dotenv()

#FastAPI 앱 초기화
app = FastAPI(title="Press Info API", description="OpenSearch 기반 기사 정보 조회 API")

# OpenSearch 연결 생성
host = os.getenv("OPENSEARCH_HOST") 
port = 443
auth = (os.getenv("OPENSEARCH_ID"), os.getenv("OPENSEARCH_PW"))

# OpenSearch 클라이언트 생성
client = OpenSearch(
    hosts=[{'host': host, 'port': port, 'scheme': 'https'}],
    http_compress=True,
    http_auth=auth,
    use_ssl=True,
    ssl_show_warn=False
)

# 조회할 인덱스 이름 설정
INDEX_NAME = "press-list-alias"

@app.get("/press/{pressId}", summary="특정 기사 데이터 조회")
async def get_press_info(
    pressId: str = Path(..., description="조회할 기사의 고유 ID")
):
    # 1. OpenSearch 검색 쿼리 작성
    # pressId 필드가 일치하는 데이터를 1건만 가져오도록 설정
    query = {
        "query": {
            "term": {
                "pressId": pressId
            }
        },
        "size":1
    }

    try:
        # 2. OpenSearch에 검색 요청
        response = client.search(
            body = query,
            index = INDEX_NAME
        )

        # 3. 검색 결과 확인
        hits = response['hits']['hits']

        # 데이터가 없을 경우 404 Not Found 에러 발생
        if not hits:
            raise HTTPException(status_code=404, detail=f"Press ID '{pressId}'를 찾을 수 없습니다.")
        
        # 데이터가 있다면 원본 데이터 반환
        return hits[0]['_source']
    
    except Exception as e:
        # OpenSearch 자체의 에러나 연결 문제 발생 시 500 에러 처리
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"서버 내부 오류: {str(e)}")