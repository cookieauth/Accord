# app/main.py

from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import logging

from app import models, crud
from app.middleware import AuthenticationMiddleware
from app.routers import auth, admin, personnel, departments, muster_reports, notifications, users, hr

app = FastAPI(debug=True)

# Mount static files
app.mount("frontend/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Add the authentication middleware.
app.add_middleware(AuthenticationMiddleware)

# Include routers
app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(departments.router)
app.include_router(hr.router)
app.include_router(muster_reports.router)
app.include_router(notifications.router)
app.include_router(personnel.router)
app.include_router(users.router)

# Create the crud tables on startup (use Alembic in production)
@app.on_event("startup")
async def startup_event():
    async with crud.engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)
    # Start any schedulers or background tasks if needed

# Root route redirects to login
@app.get("/", response_class=HTMLResponse)
async def root():
    return RedirectResponse(url="/login")
