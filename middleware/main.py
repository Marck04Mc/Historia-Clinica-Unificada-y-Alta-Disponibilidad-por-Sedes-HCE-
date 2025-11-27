"""
Aplicación principal FastAPI
Sistema de Historia Clínica Electrónica Interoperable
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager
import os

from database import db
from config import settings

# Importar routers
from routers import auth, patients, encounters, observations, fhir_adapter, pdf_export, stats, users


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestión del ciclo de vida de la aplicación"""
    # Startup
    print("🚀 Iniciando aplicación...")
    await db.connect()
    print("✓ Aplicación iniciada correctamente")
    
    yield
    
    # Shutdown
    print("🛑 Deteniendo aplicación...")
    await db.disconnect()
    print("✓ Aplicación detenida correctamente")


# Crear aplicación FastAPI
app = FastAPI(
    title="Sistema HCE Interoperable",
    description="Historia Clínica Electrónica con interoperabilidad FHIR",
    version="1.0.0",
    lifespan=lifespan
)

# Configurar CORS
origins = settings.CORS_ORIGINS.split(",") if settings.CORS_ORIGINS != "*" else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configurar archivos estáticos y templates
# Crear directorios si no existen
os.makedirs("static", exist_ok=True)
os.makedirs("templates", exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Incluir routers
app.include_router(auth.router)
app.include_router(patients.router)
app.include_router(encounters.router)
app.include_router(observations.router)
app.include_router(fhir_adapter.router)
app.include_router(pdf_export.router)
app.include_router(stats.router)
app.include_router(users.router)


# =====================================================
# Rutas de la interfaz web
# =====================================================

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Página de inicio - redirige a login"""
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Página de login"""
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/dashboard/patient", response_class=HTMLResponse)
async def patient_dashboard(request: Request):
    """Dashboard para pacientes"""
    return templates.TemplateResponse("patient_dashboard.html", {"request": request})


@app.get("/dashboard/admissions", response_class=HTMLResponse)
async def admissions_dashboard(request: Request):
    """Dashboard para admisionistas"""
    return templates.TemplateResponse("admissions_dashboard.html", {"request": request})


@app.get("/dashboard/doctor", response_class=HTMLResponse)
async def doctor_dashboard(request: Request):
    """Dashboard para médicos"""
    return templates.TemplateResponse("doctor_dashboard.html", {"request": request})


@app.get("/dashboard/records", response_class=HTMLResponse)
async def records_dashboard(request: Request):
    """Dashboard para historificación"""
    return templates.TemplateResponse("records_dashboard.html", {"request": request})


@app.get("/dashboard/admin", response_class=HTMLResponse)
async def admin_dashboard(request: Request):
    """Dashboard para administradores"""
    return templates.TemplateResponse("admin_dashboard.html", {"request": request})


@app.get("/change-password", response_class=HTMLResponse)
async def change_password_page(request: Request):
    """Página de cambio de contraseña"""
    return templates.TemplateResponse("change_password.html", {"request": request})


# =====================================================
# Endpoints de utilidad
# =====================================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "HCE Middleware",
        "version": "1.0.0"
    }


@app.get("/api/sedes")
async def list_sedes():
    """Listar todas las sedes disponibles"""
    query = "SELECT id_sede, nombre, ciudad FROM sedes WHERE activo = TRUE"
    sedes = await db.fetch_all(query)
    return sedes


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
