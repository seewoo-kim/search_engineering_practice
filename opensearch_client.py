from opensearchpy import AsyncOpenSearch
from config import settings

client = AsyncOpenSearch(
    hosts=[{'host': settings.OPENSEARCH_HOST, 'port': 443, 'scheme': 'https'}],
    http_compress=True,
    http_auth=(settings.OPENSEARCH_ID, settings.OPENSEARCH_PW),
    use_ssl=True,
    verify_certs=True,
    ssl_show_warn=False
)
