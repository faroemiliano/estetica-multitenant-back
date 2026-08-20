from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import extract
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.cliente import Cliente
from app.schemas.clientes import ClienteCreate, ClienteAdminCreate
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


@router.post("/admin/clientes")
def crear_cliente_admin(
    body: ClienteAdminCreate,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Solo un administrador puede crear clientes")

    email = body.email.lower().strip() if body.email else None
    if email and ("@" not in email or "." not in email.split("@")[-1]):
        raise HTTPException(status_code=422, detail="Ingresá un email válido")
    usuario = None

    if email:
        usuario = db.query(User).filter(User.email == email).first()
        if usuario and usuario.estetica_id != user["estetica_id"]:
            raise HTTPException(status_code=409, detail="Ese email pertenece a otra estética")
        if usuario and usuario.cliente:
            raise HTTPException(status_code=409, detail="Ya existe un cliente con ese email")

    if not usuario:
        usuario = User(
            estetica_id=user["estetica_id"],
            email=email,
            nombre=body.nombre_completo.strip(),
            role="cliente",
        )
        db.add(usuario)
        db.flush()

    nuevo_cliente = Cliente(
        user_id=usuario.id,
        estetica_id=user["estetica_id"],
        email=email,
        nombre_completo=body.nombre_completo.strip(),
        fecha_nacimiento=body.fecha_nacimiento,
        telefono=body.telefono.strip(),
        perfil_completo=True,
    )
    db.add(nuevo_cliente)
    db.commit()
    db.refresh(nuevo_cliente)
    return nuevo_cliente


def obtener_cliente_admin(cliente_id: int, user: dict, db: Session):
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Solo un administrador puede gestionar clientes")

    cliente = db.query(Cliente).filter(
        Cliente.id == cliente_id,
        Cliente.estetica_id == user["estetica_id"],
    ).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return cliente


@router.put("/admin/clientes/{cliente_id}")
def actualizar_cliente_admin(
    cliente_id: int,
    body: ClienteAdminCreate,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    cliente = obtener_cliente_admin(cliente_id, user, db)
    email = body.email.lower().strip() if body.email else None
    if email and ("@" not in email or "." not in email.split("@")[-1]):
        raise HTTPException(status_code=422, detail="Ingresá un email válido")

    if email:
        cliente_con_email = db.query(Cliente).filter(
            Cliente.email == email,
            Cliente.id != cliente.id,
        ).first()
        usuario_con_email = db.query(User).filter(
            User.email == email,
            User.id != cliente.user_id,
        ).first()
        if cliente_con_email or usuario_con_email:
            raise HTTPException(status_code=409, detail="Ya existe otro cliente con ese email")

    cliente.nombre_completo = body.nombre_completo.strip()
    cliente.telefono = body.telefono.strip()
    cliente.email = email
    cliente.fecha_nacimiento = body.fecha_nacimiento

    if cliente.user:
        cliente.user.nombre = cliente.nombre_completo
        cliente.user.email = email

    db.commit()
    db.refresh(cliente)
    return cliente


@router.delete("/admin/clientes/{cliente_id}")
def eliminar_cliente_admin(
    cliente_id: int,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    cliente = obtener_cliente_admin(cliente_id, user, db)
    db.delete(cliente)
    db.commit()
    return {"message": "Cliente eliminado"}

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
