from fastapi import FastAPI

from app.database import Base, engine
from fastapi.middleware.cors import CORSMiddleware

from app.models.cliente import Cliente
from app.models.estetica import Estetica
from app.models.user import User


from app.routes.clientes import router as clientes_router
from app.routes.estetica import router as estetica_router
from app.routes.auth import router as auth_router
from app.routes.servicios import router as servicios_router
from app.routes.turnos import router as turnos_router
from app.routes.dashboard import router as dashboard_router
from app.routes.profesionales import router as profesionales_router

Base.metadata.create_all(bind=engine)

app = FastAPI()
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173"
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

def root():
    return {"message": "API funcionando"}