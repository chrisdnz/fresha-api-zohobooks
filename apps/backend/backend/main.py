import logging

from typing import Union
from fastapi import FastAPI, Response, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from backend.database.prisma.connection import connect_db, disconnect_db
from backend.authentication.session import validate_session
from backend.routes.scheduled_jobs import sales_router
from backend.routes.zoho import zoho_router
from backend.routes.invoices import invoices_router
from backend.tasks.qstash import init_scheduler, remove_scheduler

API_PREFIX = "/api/v1"
queue = None

logging.basicConfig(level=logging.INFO)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*", "Authorization"],
)

app.include_router(sales_router, prefix=API_PREFIX)
app.include_router(zoho_router, prefix=API_PREFIX)
app.include_router(invoices_router, prefix=API_PREFIX)

@app.middleware("http")
async def verify_authorization(request: Request, call_next):
    if request.url.path.startswith(f"{API_PREFIX}/sales"):
        return await call_next(request)

    if request.method == "OPTIONS":
        response = await call_next(request)
        return response
    
    access_token = request.headers.get("Authorization")
    
    if not access_token:
        return Response(status_code=401, content="Authorization header is required")

    if not validate_session(access_token):
        return Response(status_code=401, content="Unauthorized access")
    
    response = await call_next(request)
    return response


@app.exception_handler(Exception)
async def error_handler(request: Request, exc: Union[Exception, str]):
    if isinstance(exc, Exception):
        return Response(status_code=500, content=str(exc))
    else:
        return Response(status_code=400, content=exc)


@app.on_event("startup")
async def on_startup():
    await connect_db()


@app.on_event("shutdown")
async def shutdown():
    await disconnect_db()


@app.get("/")
def main():
    return "Server is running!"
