import json
import time
import uuid
from datetime import datetime
def log(request, status, level="INFO", extra=None):
    data = {
        "ts": datetime.utcnow().isoformat() + "Z",
        "level": level,
        "request_id": str(uuid.uuid4()),
        "method": request.method,
        "path": request.url.path,
        "status": status,
        "latency_ms": int((time.time() - request.state.start) * 1000),
    }
    if extra:
        data.update(extra)
    print(json.dumps(data))