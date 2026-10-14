from fastapi import FastAPI
from pydantic import BaseModel, HttpUrl
from arq import create_pool
from arq.connections import RedisSettings
from src.config import settings

app = FastAPI(title="scraper-engine API", version="1.0.0")

class ScrapeJobRequest(BaseModel):
    url: HttpUrl
    scraper_name: str

@app.post("/api/v1/jobs")
async def enqueue_scrape_job(job: ScrapeJobRequest):
    redis = await create_pool(RedisSettings(host=settings.REDIS_HOST, port=settings.REDIS_PORT))
    task = await redis.enqueue_job("scrape_target_url", str(job.url), job.scraper_name)
    return {
        "status": "queued",
        "job_id": task.job_id,
        "url": str(job.url),
        "scraper_name": job.scraper_name,
    }