import logging
from fastapi import Request
from fastapi.responses import JSONResponse
logger = logging.getLogger(__name__)
async def unhandled_error_handler(request: Request, exc: Exception):
    request_id = getattr(request.state, "request_id", "unknown")
    logger.exception("Unhandled application error request_id=%s", request_id)
    return JSONResponse(status_code=500, content={"detail": "An unexpected server error occurred.", "request_id": request_id})
