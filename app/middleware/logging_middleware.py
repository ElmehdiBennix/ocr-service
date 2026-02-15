"""Request/response logging middleware."""

import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


class LoggingMiddleware(BaseHTTPMiddleware):
    """Log all requests and responses."""
    
    async def dispatch(self, request: Request, call_next):
        """Process and log request/response."""
        start_time = time.time()
        
        # Log request
        print(f"→ {request.method} {request.url.path}")
        
        # Process request
        response = await call_next(request)
        
        # Calculate processing time
        process_time = time.time() - start_time
        
        # Log response
        print(f"← {request.method} {request.url.path} - {response.status_code} ({process_time:.2f}s)")
        
        # Add custom headers
        response.headers["X-Process-Time"] = str(process_time)
        
        return response
