from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from app import models
from app.database import engine
from app.routes import router

# Create database tables
models.Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(title="Game Data Eval tool")

# Mount static files - ensure the directory exists
static_dir = Path("app/static")
if not static_dir.exists():
    static_dir.mkdir(parents=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Include the router
app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)  # Fixed module path