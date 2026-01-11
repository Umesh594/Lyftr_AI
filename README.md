## Overview

This project is a FastAPI based backend service built as part of the Lyftr Backend Assignment. The application securely ingests webhook messages using HMAC authentication, stores them in a SQLite database and exposes APIs for querying messages, system health and metrics.

The service is Dockerized, observable via Prometheus metrics and fully testable using Swagger UI and automated scripts.

## Tech Stack

Backend Framework: FastAPI (Python 3.11)

Database: SQLite

Authentication: HMAC-SHA256 (Webhook Security)

Metrics: Prometheus (prometheus_client)

Containerization: Docker & Docker Compose

API Docs: Swagger UI (OpenAPI)

## How to Run (Docker)
1️Build & Start Containers
docker compose up --build
2️Verify Running Containers
docker ps
3️Access API Documentation

Swagger UI: http://localhost:8000/docs

OpenAPI JSON: http://localhost:8000/openapi.json

## Webhook Authentication (HMAC)

The /webhook endpoint requires a valid HMAC-SHA256 signature.
Responses:

200 OK – Message stored successfully

401 Unauthorized – Invalid or missing signature

422 Unprocessable Entity – Validation error

GET /messages

Fetch stored messages with pagination & filters.

Query Parameters:

limit (1–100)

offset

from_ (sender MSISDN)

since (ISO timestamp)

q (search text)

Health Checks

GET /health/live= Service is running

GET /health/ready= DB & config ready

GET /metrics

Prometheus compatible metrics endpoint.

Includes:

HTTP request counts

Webhook success/failure counts

Request latency histogram

## Testing

Automated webhook test via tests/test.py

Manual testing via Swagger UI
