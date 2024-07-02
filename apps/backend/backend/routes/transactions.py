from fastapi import APIRouter
from backend.dao.invoices import get_all_invoices

from ..tasks.queue_process import scrape_transactions
from ..tasks.redis import queue, async_redis

sales_router = APIRouter()

@sales_router.get("/sales", tags=["sales"])
async def get_sales():
    invoices = await get_all_invoices()
    return {"invoices": invoices}


def background_task():
    scrape_transactions()


@sales_router.post("/sales/enqueue", tags=["sales"])
async def queue_sales():
    job = queue.enqueue(background_task)
    await async_redis.hset("jobs", job.id, "pending")
    return {"job_id": job.id}