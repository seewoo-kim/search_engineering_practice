import time
from fastapi import HTTPException, Security, Request
from fastapi.security import APIKeyHeader
from config import settings

api_key_header = APIKeyHeader(name="X-API-KEY", auto_error=True)

async def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != settings.API_KEY:
        raise HTTPException(status_code=403, detail="Could not validate credentials")
    return api_key

# In-Memory Rate Limiting
request_history = {}
RATE_LIMIT_WINDOW = 60
MAX_REQUESTS = 10

def check_rate_limit(request: Request):
    client_ip = request.client.host
    now = time.time()
    
    if client_ip not in request_history:
        request_history[client_ip] = []
    
    request_history[client_ip] = [t for t in request_history[client_ip] if now - t < RATE_LIMIT_WINDOW]
    
    if len(request_history[client_ip]) >= MAX_REQUESTS:
        raise HTTPException(status_code=429, detail="Too Many Requests. Please try again later.")
    
    request_history[client_ip].append(now)
