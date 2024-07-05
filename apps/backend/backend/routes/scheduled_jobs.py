from fastapi import APIRouter, Request
# from backend.tasks.qstash import receiver, client

from ..tasks.workers import async_task_sales_logs

sales_router = APIRouter()


@sales_router.post("/sales/list", tags=["fresha"])
async def queue_sales(request: Request):
    # signature, body = request.headers.get("Upstash-Signature"), await request.body()
    # is_valid = receiver.verify({
    #     "signature": signature,
    #     "body": body,
    #     "url": f"{request.url.scheme}://{request.url.netloc}{request.url.path}"
    # })
    await async_task_sales_logs()

    return {"message": "Sales log has been processed"}