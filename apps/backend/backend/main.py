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

@asynccontextmanager
async def lifespan(app: FastAPI):
    # await connect_db()
    # TODO: Clout deployments are extra costs, so we will not use Redis for now
    # app.state.redis = await redis_connection()
    # app.state.queue = init_queue()
    app.state.schedule_id = init_scheduler()
    try:
        yield
    finally:
        await disconnect_db()
        remove_scheduler(app.state.schedule_id)
        # await redis_disconnect(app.state.redis)


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


@app.get("/")
def main():
    return "Server is running!"
