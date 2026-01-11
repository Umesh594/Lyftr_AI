from prometheus_client import Counter, Histogram, generate_latest
http_requests = Counter(
    "http_requests_total", "HTTP Requests", ["path", "status"]
)
webhook_requests = Counter(
    "webhook_requests_total", "Webhook results", ["result"]
)
latency = Histogram("request_latency_ms", "Latency", buckets=[100, 500, float("inf")])
def metrics_response():
    return generate_latest()