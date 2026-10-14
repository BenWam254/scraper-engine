from arq.connections import RedisSettings
from src.config import settings
from src.workers.scraper_tasks import scrape_target_url

class WorkerSettings:
    functions = [scrape_target_url]
    redis_settings = RedisSettings(host=settings.REDIS_HOST, port=settings.REDIS_PORT)