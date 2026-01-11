import hmac
import hashlib
import requests
WEBHOOK_SECRET = b"testsecret"
body = b'{"message_id":"m1","from":"+919876543210","to":"+14155550100","ts":"2025-01-15T10:00:00Z","text":"Hello"}'
signature = hmac.new(WEBHOOK_SECRET, body, hashlib.sha256).hexdigest()
headers = {
    "Content-Type": "application/json",
    "X-Signature": signature
}
resp = requests.post("http://localhost:8000/webhook", headers=headers, data=body)
print(resp.status_code, resp.text)