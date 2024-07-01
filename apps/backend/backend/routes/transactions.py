from fastapi import APIRouter
from backend.dao.invoices import get_all_invoices

sales_router = APIRouter()

@sales_router.get("/sales", tags=["sales"])
async def get_sales():
    invoices = await get_all_invoices()
    return {"invoices": invoices}