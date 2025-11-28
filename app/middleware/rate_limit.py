from fastapi import Request, HTTPException
from collections import defaultdict
import time
from datetime import datetime, timedelta

request_counts = defaultdict(list)

async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host
    current_time = time.time()
    
    # Clean old requests (older than 1 minute)
    request_counts[client_ip] = [
        req_time for req_time in request_counts[client_ip] 
        if current_time - req_time < 60
    ]
    
    # Check rate limit (100 requests per minute)
    if len(request_counts[client_ip]) >= 100:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    # Add current request
    request_counts[client_ip].append(current_time)
    
    response = await call_next(request)
    return response