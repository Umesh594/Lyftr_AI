from fastapi.testclient import TestClient
from app.main import app
client = TestClient(app)
def test_stats_shape():
    r = client.get("/stats")
    assert r.status_code == 200
    body = r.json()
    assert "total_messages" in body
    assert "senders_count" in body
    assert "messages_per_sender" in body
    assert "first_message_ts" in body
    assert "last_message_ts" in body