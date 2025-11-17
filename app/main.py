from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .logging import setup_logging_middleware
from .routers import auth, habits

app = FastAPI()

# Configure CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(habits.router)

# Add middleware
setup_logging_middleware(app)

@app.get("/")
async def root():
    return {
        "message": "Welcome to Streaky Habit Tracker API",
        "documentation": "http://localhost:8002/docs",
        "endpoints": [
            "POST /habits - Create habit",
            "GET /habits - List habits with streaks",
            "POST /habits/{id}/entries - Log entry",
            "GET /habits/{id}/stats - Get habit stats",
            "GET /healthz - Health check"
        ]
    }

@app.get("/healthz")
def health_check():
    return {"ok": True}
