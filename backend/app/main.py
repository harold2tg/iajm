from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.cron.jobs import scheduler


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    scheduler.start()
    yield
    scheduler.shutdown(wait=False)
from app.domains.usuarios.router import auth_router, router as usuarios_router
from app.domains.miembros.router import router as miembros_router
from app.domains.grupos.router import router as grupos_router
from app.domains.asesores.router import router as asesores_router
from app.domains.encuentros.router import router as encuentros_router, miembros_router as encuentros_miembros_router
from app.domains.tesoreria.router import router as tesoreria_router
from app.domains.gastos.router import router as gastos_router
from app.domains.tienda.router import router as tienda_router
from app.domains.inventario.router import router as inventario_router
from app.domains.parroquial.router import router as parroquial_router
from app.domains.reportes.router import router as reportes_router

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restringir en prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(usuarios_router, prefix="/api/v1/usuarios", tags=["usuarios"])
app.include_router(miembros_router, prefix="/api/v1/miembros", tags=["miembros"])
app.include_router(grupos_router, prefix="/api/v1/grupos", tags=["grupos"])
app.include_router(asesores_router, prefix="/api/v1/asesores", tags=["asesores"])
app.include_router(encuentros_router, prefix="/api/v1/encuentros", tags=["encuentros"])
app.include_router(encuentros_miembros_router, prefix="/api/v1/miembros", tags=["miembros"])
app.include_router(tesoreria_router, prefix="/api/v1/tesoreria", tags=["tesoreria"])
app.include_router(gastos_router, prefix="/api/v1/gastos", tags=["gastos"])
app.include_router(tienda_router, prefix="/api/v1/tienda", tags=["tienda"])
app.include_router(inventario_router, prefix="/api/v1/inventario", tags=["inventario"])
app.include_router(parroquial_router, prefix="/api/v1/parroquial", tags=["parroquial"])
app.include_router(reportes_router, prefix="/api/v1/reportes", tags=["reportes"])


@app.get("/api/health")
def health_check():
    return {"status": "ok", "version": settings.APP_VERSION}
