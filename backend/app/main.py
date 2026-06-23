import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse

from .database import engine, Base, SessionLocal
from .routers import resume, analysis, roadmap, interview, internships, resources
from . import models
from .roles_database import seed_roles
from .internships_database import seed_internships
from .resources_database import seed_resources

# Ensure SQLite database tables are created on start
Base.metadata.create_all(bind=engine)

# Seed tables on startup
db = SessionLocal()
try:
    seed_roles(db)
    seed_internships(db)
    seed_resources(db)
finally:
    db.close()


app = FastAPI(
    title="Smart Career Assistant",
    description="FastAPI Backend for Phase 1 Smart Career Assistant",
    version="1.0.0"
)

# CORS middleware configuration to allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all for development. Can restrict as needed.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register backend API routers
app.include_router(resume.router)
app.include_router(analysis.router)
app.include_router(roadmap.router)
app.include_router(interview.router)
app.include_router(internships.router)
app.include_router(resources.router)

# Dynamic path resolution for mounting frontend static files
CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
FRONTEND_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "../../frontend"))

# Serve frontend HTML at root
@app.get("/")
def read_root():
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "Welcome to Smart Career Assistant API. Frontend dashboard files not found."}

# Mount css and js static directories
css_dir = os.path.join(FRONTEND_DIR, "css")
js_dir = os.path.join(FRONTEND_DIR, "js")

# Create directories if they do not exist to prevent startup errors
os.makedirs(css_dir, exist_ok=True)
os.makedirs(js_dir, exist_ok=True)

app.mount("/css", StaticFiles(directory=css_dir), name="css")
app.mount("/js", StaticFiles(directory=js_dir), name="js")
# Fallback mount for resources/images inside frontend
app.mount("/frontend", StaticFiles(directory=FRONTEND_DIR), name="frontend")
