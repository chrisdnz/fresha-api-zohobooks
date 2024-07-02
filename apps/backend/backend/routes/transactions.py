from fastapi import APIRouter, Request
from backend.dao.invoices import get_all_invoices

from ..tasks.workers import scrape_transactions, scrape_sales

sales_router = APIRouter()

@sales_router.get("/sales", tags=["sales"])
async def get_sales():
    invoices = await get_all_invoices()
    return {"invoices": invoices}


@sales_router.post("/sales/enqueue", tags=["sales"])
async def queue_sales(request: Request):
    queue = request.app.state.queue
    redis = request.app.state.redis
    job = queue.enqueue(scrape_sales)
    await redis.hset("jobs", job.id, "pending")
    return {"job_id": job.id}