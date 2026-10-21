# scraper-engine

[![CI Pipeline](https://github.com/BenWam254/scraper-engine/actions/workflows/ci.yml/badge.svg)](https://github.com/BenWam254/scraper-engine/actions)
[![Python Version](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/downloads/)
[![Package Manager](https://img.shields.io/badge/managed%20by-uv-purple.svg)](https://github.com/astral-sh/uv)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

A high-throughput, distributed web scraping engine built for asynchronous task dispatch, headless browser extraction, and real-time operational telemetry emission.

Designed as a decoupled processing layer in a distributed data platform, `scraper-engine` delegates heavy browser rendering tasks across background worker nodes using Redis and ARQ, pushing performance metrics directly to external observability sinks like `scraper-tracker`.

---

## Architecture Overview
                    │   POST /api/v1/jobs     │
                    └────────────┬────────────┘
                                 │
                                 ▼
                      ┌─────────────────────┐
                      │   FastAPI Master    │
                      │   (Port 8001)       │
                      └──────────┬──────────┘
                                 │
                         Enqueue │ Task
                                 ▼
                      ┌─────────────────────┐
                      │     Redis Queue     │
                      │     (Port 6379)     │
                      └──────────┬──────────┘
                                 │
                         Consume │ Job
                                 ▼
                      ┌─────────────────────┐
                      │  ARQ Worker Nodes   │
                      │  (Crawl4AI Engine)  │
                      └──────────┬──────────┘
                                 │
                     Emit Telemetry (HTTP POST)
                                 ▼
                      ┌─────────────────────┐
                      │   scraper-tracker   │
                      │   (Port 8000)       │
                      └─────────────────────┘

---

## Key Features

* **Asynchronous Task Queue:** High-concurrency task dispatch using **ARQ** and **Redis** for non-blocking job creation.
* **Modern Headless Browser Extraction:** Renders dynamic, JavaScript-heavy single-page applications using **Crawl4AI** and **Playwright (Chromium)** into structured Markdown payloads.
* **Integrated Telemetry Emitter:** Automatically emits request latency, HTTP status codes, item counts, and failure tracking to `scraper-tracker` post-execution.
* **Resilient Defensive Execution:** Features localized exception handling to ensure network timeouts or bad HTTP targets do not collapse background worker threads.
* **Container-First Orchestration:** Multi-stage Docker build with pre-packaged Chromium binaries and a multi-service Docker Compose environment.
* **Automated CI/CD:** Continuous Integration workflow executing headless browser test suites against live Redis services via GitHub Actions.

---

## Tech Stack

* **Language & Tooling:** Python 3.13, `uv` package manager
* **API Framework:** FastAPI, Uvicorn, Pydantic v2
* **Queue & Cache:** Redis 7 (Alpine), ARQ (Async Redis Queue)
* **Web Scraping Engine:** Crawl4AI (v0.9.4+), Playwright
* **HTTP Client:** `httpx`
* **Testing Framework:** Pytest, `pytest-asyncio`
* **Infrastructure:** Docker Compose, GitHub Actions CI

---

## Repository Structure

scraper-engine/
├── .github/
│   └── workflows/
│       └── ci.yml             # GitHub Actions CI workflow
├── src/
│   ├── init.py
│   ├── api.py                 # FastAPI master endpoint for job dispatch
│   ├── config.py              # Environment variables & runtime settings
│   ├── queue.py               # Redis connection settings & ARQ config
│   ├── tracker_client.py      # Async telemetry emitter client
│   └── workers/
│       ├── init.py
│       └── scraper_tasks.py   # Crawl4AI worker execution logic
├── tests/
│   └── test_engine.py         # Unit & integration test suite
├── docker-compose.yml         # Service orchestration stack
├── Dockerfile                 # Multi-stage container definition
├── pyproject.toml             # Project setup and dependency specs
└── uv.lock                    # Deterministic lockfile


---

## Quick Start (Local Development)

### Prerequisites

* [Python 3.13+](https://www.python.org/)
* [`uv` package manager](https://github.com/astral-sh/uv)
* [Docker Desktop](https://www.docker.com/)

### 1. Clone & Setup Environment

```bash
git clone [https://github.com/BenWam254/scraper-engine.git](https://github.com/BenWam254/scraper-engine.git)
cd scraper-engine
```

## Sync dependencies with uv

```bash
uv sync
```

## Install Playwright Chromium dependencies

```bash
uv run crawl4ai-setup
```

## Start Infrastructure Services
Start the local Redis instance using Docker Compose:

```bash
docker compose up -d redis
```

## Run Application Services
Open two separate terminal windows:

Terminal 1 — ARQ Worker Node:

```bash
uv run arq src.queue.WorkerSettings
```

### Terminal 2 — FastAPI Master API:

```bash
uv run uvicorn src.api:app --reload --port 8001
```

### API Reference
Enqueue Scraping Job
URL: /api/v1/jobs

Method: POST

Headers: Content-Type: application/json

### Request Payload

```bash
{
  "url": "[https://news.ycombinator.com](https://news.ycombinator.com)",
  "scraper_name": "hn_bot"
}
```

### Success Response (200 OK)

```bash
{
  "status": "queued",
  "job_id": "a51e606b516c4700bbc89b729a51735e",
  "url": "[https://news.ycombinator.com/](https://news.ycombinator.com/)",
  "scraper_name": "hn_bot"
}
```

### Docker Compose Deployment
To build and run the full stack (Redis, API Master, and Worker Nodes) inside isolated containers:

```bash
docker compose up --build -d
```

The API will be available at http://localhost:8001, with interactive OpenAPI documentation at http://localhost:8001/docs.

### Testing & CI
The repository maintains unit and integration coverage using pytest.

Run the test suite locally:

```bash
uv run pytest -v
```

### CI Pipeline
Every push or pull request to main triggers a GitHub Actions workflow that:

Provisions a Redis 7 service container.

Sets up Python 3.13 and caches dependencies using uv.

Installs Playwright Chromium browser binaries inside the runner.

Executes the pytest test suite.

### License
This project is open-source software licensed under the MIT License.
