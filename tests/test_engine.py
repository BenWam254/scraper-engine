import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient

from src.api import app
from src.workers.scraper_tasks import scrape_target_url

client = TestClient(app)


def test_enqueue_job_endpoint():
    """Verify POST /api/v1/jobs successfully queues a scrape task."""
    payload = {
        "url": "https://example.com",
        "scraper_name": "pytest_verification_bot"
    }

    with patch("src.api.create_pool") as mock_create_pool:
        mock_redis = AsyncMock()
        mock_task = AsyncMock()
        mock_task.job_id = "test_job_12345"
        mock_redis.enqueue_job.return_value = mock_task
        mock_create_pool.return_value = mock_redis

        response = client.post("/api/v1/jobs", json=payload)

        assert response.status_code == 200
        assert response.json()["status"] == "queued"
        assert response.json()["job_id"] == "test_job_12345"
        assert response.json()["scraper_name"] == "pytest_verification_bot"


def test_enqueue_job_invalid_url():
    """Verify POST /api/v1/jobs rejects malformed URLs with a 422 error."""
    payload = {
        "url": "not-a-valid-url",
        "scraper_name": "invalid_bot"
    }
    response = client.post("/api/v1/jobs", json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_scrape_target_url_worker_task():
    """Verify the worker task executes crawler logic and dispatches telemetry."""
    mock_ctx = {}
    target_url = "https://example.com"
    scraper_name = "test_worker_bot"

    with patch("src.workers.scraper_tasks.AsyncWebCrawler") as mock_crawler_cls, \
         patch("src.workers.scraper_tasks.send_telemetry") as mock_telemetry:

        mock_crawler_instance = AsyncMock()
        mock_result = AsyncMock()
        mock_result.success = True
        mock_result.status_code = 200

        # Mock Crawl4AI 0.9.4+ markdown object
        mock_markdown = AsyncMock()
        mock_markdown.raw_markdown = "# Title\nLine 1\nLine 2"
        mock_result.markdown = mock_markdown

        mock_crawler_instance.arun.return_value = mock_result
        mock_crawler_cls.return_value.__aenter__.return_value = mock_crawler_instance

        result = await scrape_target_url(mock_ctx, url=target_url, scraper_name=scraper_name)

        assert result["url"] == target_url
        assert result["status_code"] == 200
        assert result["items_extracted"] == 3
        mock_telemetry.assert_called_once()