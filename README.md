/project-root

    2 ├── fastapi_practice.py      # 메인 진입점 (모듈 조립 및 엔드포인트 정의)

    3 ├── config.py            # 환경 변수 및 공통 설정 관리

    4 ├── database.py          # DB 엔진 및 세션 관리 (get_db)

    5 ├── models.py            # DB 테이블 정의 (PressList)

    6 ├── schemas.py           # Pydantic 응답 모델 정의 (PressListResponse)

    7 ├── dependencies.py      # 인증 및 속도 제한 로직

    8 ├── opensearch_client.py # OpenSearch 클라이언트 초기화