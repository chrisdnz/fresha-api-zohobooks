from fastapi import APIRouter, Request

from backend.dao.invoices import get_all_invoices

invoices_router = APIRouter()

@invoices_router.get("/invoices")
async def get_invoices(request: Request):
    return await get_all_invoices()