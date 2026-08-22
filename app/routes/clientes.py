from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import extract
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.cliente import Cliente
from app.schemas.clientes import ClienteCreate, ClienteAdminCreate
from app.dependencies import get_current_user, require_admin
from app.models.membership import Membership
from app.models.user import User
from app.models.turno import Turno


router = APIRouter()

@router.get("/clientes")
def obtener_clientes(
    user = Depends(require_admin),
    db: Session = Depends(get_db)
):

    clientes = db.query(Cliente).filter(
        Cliente.estetica_id == user["estetica_id"]
    ).all()

    return clientes

@router.post("/clientes")
def crear_cliente(
    cliente: ClienteCreate,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):

    existente = db.query(Cliente).filter(
        Cliente.user_id == int(user["sub"]),
        Cliente.estetica_id == user["estetica_id"],
    ).first()
    if existente:
        raise HTTPException(status_code=409, detail="El perfil ya existe")

    nuevo_cliente = Cliente(
        user_id=int(user["sub"]),
        estetica_id=user["estetica_id"],
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
    user=Depends(require_admin),
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
        if usuario and db.query(Cliente).filter(
            Cliente.user_id == usuario.id,
            Cliente.estetica_id == user["estetica_id"],
        ).first():
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

    membership = db.query(Membership).filter(
        Membership.user_id == usuario.id,
        Membership.estetica_id == user["estetica_id"],
    ).first()
    if not membership:
        db.add(Membership(
            user_id=usuario.id,
            estetica_id=user["estetica_id"],
            role="cliente",
        ))

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
    user=Depends(require_admin),
    db: Session = Depends(get_db),
):
    cliente = obtener_cliente_admin(cliente_id, user, db)
    email = body.email.lower().strip() if body.email else None
    if email and ("@" not in email or "." not in email.split("@")[-1]):
        raise HTTPException(status_code=422, detail="Ingresá un email válido")

    if email:
        cliente_con_email = db.query(Cliente).filter(
            Cliente.email == email,
            Cliente.estetica_id == user["estetica_id"],
            Cliente.id != cliente.id,
        ).first()
        if cliente_con_email:
            raise HTTPException(status_code=409, detail="Ya existe otro cliente con ese email")

    cliente.nombre_completo = body.nombre_completo.strip()
    cliente.telefono = body.telefono.strip()
    cliente.email = email
    cliente.fecha_nacimiento = body.fecha_nacimiento

    db.commit()
    db.refresh(cliente)
    return cliente


@router.delete("/admin/clientes/{cliente_id}")
def eliminar_cliente_admin(
    cliente_id: int,
    user=Depends(require_admin),
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
        , Cliente.estetica_id == user["estetica_id"]
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
        , Cliente.estetica_id == user["estetica_id"]
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

        estetica_id=user["estetica_id"],

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
    user=Depends(require_admin),
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
