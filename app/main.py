from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    ADMIN_KEY: str = "changeme-admin"
    SECRET_KEY: str = "changeme-secret"
    TZ: str = "Asia/Ho_Chi_Minh"
    ORG_NAME: str = "Sao Viet IT"

    class Config:
        env_file = ".env"

settings = Settings()

app = FastAPI(title=f"{settings.ORG_NAME} - Teacher Attendance")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

# Include routers
from app.routers import teacher, admin, qr
app.include_router(teacher.router)
app.include_router(admin.router)
app.include_router(qr.router)


@app.get("/", response_class=HTMLResponse)
def health(request: Request):
    return templates.TemplateResponse("base.html", {"request": request, "title": "Health", "content": "OK"})


# Startup: init DB + seed
try:
    from app.seed import create_all, seed

    @app.on_event("startup")
    def _startup():
        create_all()
        seed()
except Exception:
    pass
