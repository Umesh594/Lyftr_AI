from fastapi.testclient import TestClient
from app.main import app
client = TestClient(app)
def test_messages_basic():
    r = client.get("/messages")
    assert r.status_code == 200
    body = r.json()
    assert "data" in body
    assert "total" in body
    assert "limit" in body
    assert "offset" in body