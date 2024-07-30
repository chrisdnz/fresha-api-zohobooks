from fastapi import APIRouter, Request, Query
# from backend.tasks.qstash import receiver, client

from ..tasks.workers import async_task_sales_logs, scrape_transactions

sales_router = APIRouter()


@sales_router.post("/sales/payments", tags=["fresha"])
async def queue_sales_payments(request: Request, time_filter: str = Query(None)) :
    # signature, body = request.headers.get("Upstash-Signature"), await request.body()
    # is_valid = receiver.verify({
    #     "signature": signature,
    #     "body": body,
    #     "url": f"{request.url.scheme}://{request.url.netloc}{request.url.path}"
    # })
    time_filter = request.query_params.get("time_filter")
    await scrape_transactions({
        "time_filter": time_filter
    })

    return {"message": "Sales log has been processed"}


@sales_router.post("/sales/list", tags=["fresha"])
async def queue_sales(request: Request, time_filter: str = Query(None)) :
    # signature, body = request.headers.get("Upstash-Signature"), await request.body()
    # is_valid = receiver.verify({
    #     "signature": signature,
    #     "body": body
    # })
    time_filter = request.query_params.get("shortcut")
    date_from = request.query_params.get("dateFrom")
    date_to = request.query_params.get("dateTo")
    await async_task_sales_logs({
        "shortcut": time_filter,
        "dateFrom": date_from,
        "dateTo": date_to
    })

    return {"message": "Sales log has been processed"}