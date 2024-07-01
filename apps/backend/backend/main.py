import logging

from typing import Union
from fastapi import FastAPI, Response, Request
from fastapi.middleware.cors import CORSMiddleware
from playwright.sync_api import sync_playwright
from contextlib import asynccontextmanager

from .scrapping.fresha import FreshaScrapper

from .database.prisma.connection import connect_db, disconnect_db
from .routes.transactions import sales_router
from .routes.zoho import zoho_router

API_PREFIX = "/api/v1"

logging.basicConfig(level=logging.INFO)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_db()
    try:
        yield
    finally:
        await disconnect_db()


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*", "Authorization"],
)

app.include_router(sales_router, prefix=API_PREFIX)
app.include_router(zoho_router, prefix=API_PREFIX)

@app.middleware("http")
async def verify_authorization(request: Request, call_next):
    if request.method == "OPTIONS":
        response = await call_next(request)
        return response
    
    access_token = request.headers.get("Authorization")
    if not access_token:
        return Response(status_code=401, content="Authorization header is required")
    
    response = await call_next(request)
    return response


@app.exception_handler(Exception)
async def error_handler(request: Request, exc: Union[Exception, str]):
    if isinstance(exc, Exception):
        return Response(status_code=500, content=str(exc))
    else:
        return Response(status_code=400, content=exc)


@app.get("/")
def main():
    return "Server is running!"


@app.get("/fresha/sales")
def list_sales():
    # TODO: Implement Fresha sales list
    with sync_playwright() as p:
        fresha = FreshaScrapper(p)
        fresha.authenticate()
        fresha.get_payment_transactions()
        return {"sales": "Work in progress"}
