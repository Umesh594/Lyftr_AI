import hmac
import hashlib
import time
import sqlite3
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.config import WEBHOOK_SECRET
from app.models import init_db, get_db
from app.storage import insert_message, list_messages, stats
from app.logging_utils import log
from app.metrics import http_requests, webhook_requests, latency, metrics_response
E164_pattern = r"^\+\d+$"
app = FastAPI()
@app.on_event("startup")
def startup():
    if not WEBHOOK_SECRET:
        return
    init_db()
@app.middleware("http")
async def middleware(request: Request, call_next):
    request.state.start = time.time()
    response = await call_next(request)
    http_requests.labels(path=request.url.path, status=response.status_code).inc()
    latency.observe((time.time() - request.state.start) * 1000)
    return response
class WebhookMsg(BaseModel):
    message_id: str = Field(..., min_length=1)
    from_: str = Field(..., alias="from", pattern=E164_pattern)
    to: str = Field(..., pattern=E164_pattern)
    ts: datetime
    text: Optional[str] = Field(None, max_length=4096)
@app.post("/webhook")
async def webhook(request: Request):
    raw = await request.body()
    sig = request.headers.get("X-Signature")
    if not WEBHOOK_SECRET or not sig:
        webhook_requests.labels("invalid_signature").inc()
        log(request, 401, level="ERROR", extra={"result": "invalid_signature"})
        raise HTTPException(status_code=401, detail="invalid signature")
    expected = hmac.new(
        WEBHOOK_SECRET.encode(), raw, hashlib.sha256
    ).hexdigest()
    if not hmac.compare_digest(sig, expected):
        webhook_requests.labels("invalid_signature").inc()
        log(request, 401, level="ERROR", extra={"result": "invalid_signature"})
        raise HTTPException(status_code=401, detail="invalid signature")
    try:
        payload = WebhookMsg.model_validate_json(raw)
    except Exception:
        webhook_requests.labels("validation_error").inc()
        log(request, 422, level="ERROR", extra={"result": "validation_error"})
        raise
    result = insert_message(payload.model_dump(by_alias=True))
    webhook_requests.labels(result).inc()
    log(
        request,
        200,
        extra={
            "message_id": payload.message_id,
            "dup": result == "duplicate",
            "result": result,
        },
    )
    return {"status": "ok"}
@app.get("/messages")
def messages(
    limit: int = 50,
    offset: int = 0,
    from_: Optional[str] = None,
    since: Optional[str] = None,
    q: Optional[str] = None,
):
    limit = min(max(limit, 1), 100)
    filters = {"from": from_, "since": since, "q": q}
    total, data = list_messages(filters, limit, offset)
    return {"data": data, "total": total, "limit": limit, "offset": offset}
@app.get("/stats")
def stats_endpoint():
    return stats()
@app.get("/health/live")
def live():
    return {"status": "ok"}
@app.get("/health/ready")
def ready():
    if not WEBHOOK_SECRET:
        raise HTTPException(status_code=503)
    try:
        conn = get_db()
        conn.execute("SELECT 1")
        conn.close()
    except sqlite3.Error:
        raise HTTPException(status_code=503)

    return {"status": "ready"}
@app.get("/metrics")
def metrics():
    return PlainTextResponse(metrics_response())