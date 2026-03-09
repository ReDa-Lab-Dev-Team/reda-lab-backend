from fastapi import Request
from starlette.responses import JSONResponse
from collections import defaultdict
import time

# In-memory rate limiter with cleanup
request_counts = defaultdict(list)
MAX_REQUESTS = 100
WINDOW_SECONDS = 60
CLEANUP_THRESHOLD = 1000  # Clean up IPs when dict gets too large

async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host if request.client else "unknown"
    print(f"Client IP: {client_ip}")
    current_time = time.time()
    
    # Periodic cleanup of old IPs (prevent memory leak)
    if len(request_counts) > CLEANUP_THRESHOLD:
        for ip in list(request_counts.keys()):
            request_counts[ip] = [
                t for t in request_counts[ip] 
                if current_time - t < WINDOW_SECONDS
            ]
            if not request_counts[ip]:
                del request_counts[ip]
    
    # Clean old requests for current IP
    request_counts[client_ip] = [
        req_time for req_time in request_counts[client_ip] 
        if current_time - req_time < WINDOW_SECONDS
    ]
    
    # Check rate limit
    if len(request_counts[client_ip]) >= MAX_REQUESTS:
        return JSONResponse(
            status_code=429,
            content={
                "detail": f"Rate limit exceeded. Max {MAX_REQUESTS} requests per {WINDOW_SECONDS} seconds."
            }
        )
    
    # Add current request
    request_counts[client_ip].append(current_time)
    
    response = await call_next(request)
    return response






## Production-ready rate limiting middleware using Redis

# from fastapi import Request
# from starlette.responses import JSONResponse
# import redis
# import time

# # Connect to Redis
# redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# MAX_REQUESTS = 100
# WINDOW_SECONDS = 60

# async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host if request.client else "unknown"
    key = f"rate_limit:{client_ip}"
    
    try:
        # Increment counter
        current = redis_client.incr(key)
        
        # Set expiry on first request
        if current == 1:
            redis_client.expire(key, WINDOW_SECONDS)
        
        # Check limit
        if current > MAX_REQUESTS:
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded"}
            )
        
        response = await call_next(request)
        return response
        
    except redis.ConnectionError:
        # Fail open if Redis is down
        return await call_next(request)