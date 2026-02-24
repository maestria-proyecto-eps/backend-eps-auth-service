from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.logger import setup_logging, get_logger

app = FastAPI(
    title="EPS API 2",
    description="EPS management API 2",
    version="0.1"
)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

setup_logging()

# Logger call example
#logger = get_logger(__name__)

@app.get("/")
def root():
    """Root endpoint"""
    #logger.info("Root endpoint called")
    return {
        "message": "EPS API",
        "features": [
            "EPS management API"
        ],
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/health")
def root():
    """health endpoint"""
    return {
        "message": "ok"
    }
