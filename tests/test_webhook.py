import hmac
import hashlib
from fastapi.testclient import TestClient
from app.main import app
from app.config import WEBHOOK_SECRET
client = TestClient(app)
BODY = {
    "message_id": "m1",
    "from": "+919876543210",
    "to": "+14155550100",
    "ts": "2025-01-15T10:00:00Z",
    "text": "Hello"
}
def sign(body: str):
    return hmac.new(
        WEBHOOK_SECRET.encode(),
        body.encode(),
        hashlib.sha256
    ).hexdigest()
def test_invalid_signature():
    r = client.post("/webhook", json=BODY, headers={"X-Signature": "bad"})
    assert r.status_code == 401
def test_valid_and_duplicate():
    import json
    raw = json.dumps(BODY)
    sig = sign(raw)
    r1 = client.post("/webhook", data=raw, headers={
        "Content-Type": "application/json",
        "X-Signature": sig
    })
    assert r1.status_code == 200
    r2 = client.post("/webhook", data=raw, headers={
        "Content-Type": "application/json",
        "X-Signature": sig
    })
    assert r2.status_code == 200