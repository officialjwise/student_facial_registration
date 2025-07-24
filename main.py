from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routers import students, auth, admin, colleges, departments
from contextlib import asynccontextmanager
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
def lifespan(app: FastAPI):
    logger.info("Application startup")
    yield
    # You can add shutdown logic here if needed

app = FastAPI(
    title="KNUST Student Registration and Recognition System",
    description="RESTful API for student registration and facial recognition",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict to frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(students.router)
app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(colleges.router)
app.include_router(departments.router)

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint for health check."""
    logger.info("Root endpoint accessed")
    return {"message": "KNUST Student Registration and Recognition System"}