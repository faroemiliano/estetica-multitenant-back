from fastapi import FastAPI
from sqlalchemy import text

from fastapi.middleware.cors import CORSMiddleware

import app.models  # Registra todos los modelos en el metadata de SQLAlchemy.

from app.models.cliente import Cliente
from app.models.estetica import Estetica
from app.models.user import User
from app.database import engine


from app.routes.clientes import router as clientes_router
from app.routes.estetica import router as estetica_router
from app.routes.auth import router as auth_router
from app.routes.servicios import router as servicios_router
from app.routes.turnos import router as turnos_router
from app.routes.dashboard import router as dashboard_router
from app.routes.profesionales import router as profesionales_router

app = FastAPI()


@app.on_event("startup")
def actualizar_esquema_multitenant():
    """Migración idempotente para instalaciones existentes sin Alembic."""
    with engine.begin() as connection:
        connection.execute(text(
            "ALTER TABLE esteticas "
            "ADD COLUMN IF NOT EXISTS activo BOOLEAN NOT NULL DEFAULT TRUE"
        ))
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://estetica-multitenant.vercel.app",
]

app.add_middleware(
    CORSMiddleware,

    allow_origins=origins,

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],
)

app.include_router(estetica_router)
app.include_router(auth_router)
app.include_router(clientes_router)
app.include_router(servicios_router)
app.include_router(turnos_router)
app.include_router(dashboard_router)
app.include_router(profesionales_router)

@app.get("/")
def root():
    return {"message": "API funcionando"}
