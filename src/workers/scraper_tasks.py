import time
import logging
from crawl4ai import AsyncWebCrawler
from src.tracker_client import send_telemetry

logger = logging.getLogger("scraper_worker")

async def scrape_target_url(ctx: dict, url: str, scraper_name: str) -> dict:
    """ARQ async worker task to execute web extraction via Crawl4AI
    and automatically dispatch performance metrics to scraper-tracker.
    """
    start_time = time.perf_counter()
    status_code = 500
    items_extracted = 0
    items_failed = 0

    async with AsyncWebCrawler(verbose=False) as crawler:
        try:
            result = await crawler.arun(url=url)
            elapsed_time_ms = round((time.perf_counter() - start_time) * 1000, 2)

            if result.success:
                status_code = result.status_code or 200
                # Crawl4AI 0.9.4+ uses result.markdown.raw_markdown
                if hasattr(result, "markdown") and result.markdown:
                    raw_md = getattr(result.markdown, "raw_markdown", str(result.markdown))
                    items_extracted = len(raw_md.splitlines())
                else:
                    items_extracted = 1
            else:
                status_code = result.status_code or 500
                items_failed = 1

        except Exception as err:
            elapsed_time_ms = round((time.perf_counter() - start_time) * 1000, 2)
            logger.error(f"Scrape task failed for {url}: {err}")
            items_failed = 1

    await send_telemetry(
        scraper_name=scraper_name,
        response_time_ms=elapsed_time_ms,
        http_status_code=status_code,
        items_extracted=items_extracted,
        items_failed=items_failed,
    )

    return {
        "url": url,
        "status_code": status_code,
        "response_time_ms": elapsed_time_ms,
        "items_extracted": items_extracted,
    }