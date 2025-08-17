import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import endpoints
from app.db.database import Base, engine

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def create_db_and_tables():
    """
    Creates the database and all necessary tables defined in the ORM models.
    This function is called on application startup.
    """
    logging.info("Creating database and tables...")
    try:
        Base.metadata.create_all(bind=engine)
        logging.info("Database and tables created successfully.")
    except Exception as e:
        logging.error(f"Error creating database tables: {e}", exc_info=True)
        raise

# Create the FastAPI app instance
app = FastAPI(
    title="Enterprise RAG API",
    description="An API for a company's internal smart assistant, powered by RAG.",
    version="1.0.0",
)

# Add a startup event handler
@app.on_event("startup")
def on_startup():
    """
    Event handler for application startup.
    """
    create_db_and_tables()

# Add CORS middleware to allow cross-origin requests
# This is crucial for a decoupled frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development. Restrict in production.
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

# Include the API router
app.include_router(endpoints.router, prefix="/api", tags=["Chat and Conversations"])

# Root endpoint for health checks
@app.get("/", tags=["Health Check"])
def read_root():
    """
    Root endpoint to check if the service is running.
    """
    return {"status": "ok", "message": "Welcome to the Enterprise RAG API!"}
