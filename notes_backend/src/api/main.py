from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import router
from .database import Base, engine

openapi_tags = [
    {"name": "authentication", "description": "User registration and login"},
    {"name": "notes", "description": "CRUD and search for user notes"},
]

app = FastAPI(
    title="Notes API",
    description="API for notes application: user authentication, notes CRUD, and search",
    version="0.1.0",
    openapi_tags=openapi_tags,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    """Create tables in database on startup."""
    Base.metadata.create_all(bind=engine)

@app.get("/", tags=["authentication"])
def health_check():
    """Health check endpoint."""
    return {"message": "Healthy"}

# Include all API routes
app.include_router(router)
