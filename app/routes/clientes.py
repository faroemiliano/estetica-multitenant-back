from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import extract
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.cliente import Cliente
from app.schemas.clientes import ClienteCreate
from app.dependencies import get_current_user
from app.models.user import User
from app.models.turno import Turno


router = APIRouter()

# conexión db
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/clientes")
def obtener_clientes(
    user = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    clientes = db.query(Cliente).filter(
        Cliente.estetica_id == user["estetica_id"]
    ).all()

    return clientes

@router.post("/clientes")
def crear_cliente(cliente: ClienteCreate, db: Session = Depends(get_db)):

    nuevo_cliente = Cliente(
        estetica_id=cliente.estetica_id,
        nombre_completo=cliente.nombre_completo,
        fecha_nacimiento=cliente.fecha_nacimiento,
        telefono=cliente.telefono
    )

    db.add(nuevo_cliente)
    db.commit()
    db.refresh(nuevo_cliente)

    return {
        "message": "Cliente creado",
        "cliente_id": nuevo_cliente.id
    }

@router.get("/mi-perfil")
def obtener_mi_perfil(
    user = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    cliente = db.query(Cliente).filter(
        Cliente.user_id == int(user["sub"])
    ).first()

    if not cliente:

        raise HTTPException(
            status_code=404,
            detail="Perfil incompleto"
        )

    return cliente



@router.post("/completar-perfil")
def completar_perfil(
    body: ClienteCreate,
    user = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    cliente_existente = db.query(Cliente).filter(
        Cliente.user_id == int(user["sub"])
    ).first()

    # YA EXISTE
    if cliente_existente:

        return {
            "message": "Perfil ya completo"
        }

    usuario = db.query(User).filter(
        User.id == int(user["sub"])
    ).first()

    nuevo_cliente = Cliente(

        user_id=usuario.id,

        estetica_id=usuario.estetica_id,

        nombre_completo=body.nombre_completo,

        fecha_nacimiento=body.fecha_nacimiento,

        telefono=body.telefono,

        email=usuario.email,

        perfil_completo=True
    )

    db.add(nuevo_cliente)

    db.commit()

    db.refresh(nuevo_cliente)

    return nuevo_cliente

@router.get("/clientes/cumpleanios")
def clientes_cumpleanios(
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    hoy = date.today()

    clientes = (
        db.query(Cliente)
        .filter(
            Cliente.estetica_id == user["estetica_id"],
            Cliente.fecha_nacimiento.isnot(None),
            extract("day", Cliente.fecha_nacimiento) == hoy.day,
            extract("month", Cliente.fecha_nacimiento) == hoy.month,
        )
        .all()
    )

    return clientes