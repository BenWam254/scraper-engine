import httpx
import logging
from src.config import settings

logger = logging.getLogger("tracker_client")

async def send_telemetry(
        scraper_name: str,
        response_time_ms: float,
        http_status_code: int, 
        items_extracted: int,
        items_failed: int = 0,
):

    payload = {
        "scraper_name": scraper_name,
        "response_time_ms": response_time_ms,
        "http_status_code": http_status_code,
        "items_extracted": items_extracted,
        "items_failed": items_failed,
    }
    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            res = await client.post(settings.TRACKER_API_URL, json=payload)
            res.raise_for_status()
            logger.info(f"Telemetry dispatched for {scraper_name}")
        except Exception as e:
            logger.error(f"Failed to push telemetry to scraper-tracker: {e}")