from opensearchpy import OpenSearch

# 1. 링크 주소를 쪼개서 명확히 지정합니다.
# 주의: "https://" 부분은 빼고 순수 도메인이나 IP만 적어주세요!
# (예: dev-search.company.com)
host = "search-opensearch-dev-cluster-qpykuqoky4f6hzpjmjn6wyg43q.aos.ap-northeast-2.on.aws" 

# 링크 끝에 별도의 숫자가 없었다면 HTTPS 기본 포트인 443을 사용합니다.
# (만약 링크 끝에 :9200 이 있었다면 9200으로 적어주세요)
port = 443

auth = ('bioresearchai', 'Bio290!!')

# 클라이언트 초기화 (명시적 선언 방식)
client = OpenSearch(
    hosts=[{'host': host, 'port': port, 'scheme': 'https'}], # 이렇게 쪼개서 넣습니다.
    http_compress=True,
    http_auth=auth,
    use_ssl=True,
    ssl_show_warn=False
)
