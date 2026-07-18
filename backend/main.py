from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from backend.config.settings import settings
from backend.database.postgres import engine, Base
from backend.utils.logger import get_logger
from backend.utils.exceptions import InvalidDocumentError, DatabaseOperationError, LLMTimeoutError
from backend.utils.metrics import record_metric
from backend.api.routes import router as api_router
from backend.api.integrations import router as integrations_router
import time

logger = get_logger(__name__)

# Create database tables (For MVP, we use Base.metadata.create_all instead of Alembic migrations)
logger.info("Initializing database schema...")
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API for the AI Recruiter Assistant MVP using LangGraph orchestration.",
    version="1.0.0"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    record_metric("api_latency", process_time)
    response.headers["X-Process-Time"] = str(process_time)
    return response

# Exception Handlers
@app.exception_handler(InvalidDocumentError)
async def invalid_document_exception_handler(request: Request, exc: InvalidDocumentError):
    logger.error(f"InvalidDocumentError: {exc.message}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": exc.message},
    )

@app.exception_handler(DatabaseOperationError)
async def database_operation_exception_handler(request: Request, exc: DatabaseOperationError):
    logger.error(f"DatabaseOperationError: {exc.message}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": exc.message},
    )

@app.exception_handler(LLMTimeoutError)
async def llm_timeout_exception_handler(request: Request, exc: LLMTimeoutError):
    logger.error(f"LLMTimeoutError: {exc.message}")
    return JSONResponse(
        status_code=status.HTTP_504_GATEWAY_TIMEOUT,
        content={"detail": exc.message},
    )

# Include Routers
app.include_router(api_router, prefix=settings.API_V1_STR)
app.include_router(integrations_router, prefix=f"{settings.API_V1_STR}/integrations", tags=["integrations"])

@app.get("/")
def read_root():
    return {"message": "AI Recruiter Assistant API is running"}
