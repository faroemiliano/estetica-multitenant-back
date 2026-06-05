from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.orm import Session, joinedload

from app.database import SessionLocal

from app.models.servicio import Servicio

from app.schemas.servicio import ServicioCreate, ServicioUpdate, ServicioOut
from app.dependencies import get_current_user
from app.models.estetica import Estetica
from app.models.profesional import Profesional

router = APIRouter()

def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()

@router.post("/servicios")
def crear_servicio(
    body: ServicioCreate,
    user = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    servicio = Servicio(
        estetica_id=user["estetica_id"],
        nombre=body.nombre,
        descripcion=body.descripcion,
        duracion=body.duracion,
        precio=body.precio,
        profesional_id=body.profesional_id
    )

    profesional = (
    db.query(Profesional)
    .filter(
        Profesional.id == body.profesional_id,
        Profesional.estetica_id == user["estetica_id"]
    )
    .first()
    )

    if not profesional:
        raise HTTPException(
            status_code=400,
            detail="Profesional inválida"
        )

    db.add(servicio)

    db.commit()

    db.refresh(servicio)

    return servicio

@router.get("/servicios", response_model=list[ServicioOut])
def obtener_servicios(

    user = Depends(get_current_user),

    db: Session = Depends(get_db)
):

    servicios = (
    db.query(Servicio)
    .options(
        joinedload(Servicio.profesional)
    )
    .filter(
        Servicio.estetica_id == user["estetica_id"],
        Servicio.activo == True
    )
    .all()
)

    return servicios

@router.put("/servicios/{id}")
def editar_servicio(

    id: int,

    body: ServicioUpdate,

    user = Depends(get_current_user),

    db: Session = Depends(get_db)
):

    servicio = db.query(
        Servicio
    ).filter(
        Servicio.id == id
    ).first()

    if not servicio:

        raise HTTPException(
            status_code=404,
            detail="Servicio no encontrado"
        )

    if (
        servicio.estetica_id
        != user["estetica_id"]
    ):

        raise HTTPException(
            status_code=403,
            detail="Sin permisos"
        )

    servicio.nombre =body.nombre

    servicio.descripcion =body.descripcion

    servicio.duracion =body.duracion

    servicio.precio =body.precio

    servicio.profesional_id =body.profesional_id

    db.commit()

    db.refresh(servicio)

    return servicio

@router.delete("/servicios/{id}")
def eliminar_servicio(

    id: int,

    user = Depends(get_current_user),

    db: Session = Depends(get_db)
):

    servicio = db.query(
        Servicio
    ).filter(
        Servicio.id == id
    ).first()

    if not servicio:

        raise HTTPException(
            status_code=404,
            detail="Servicio no encontrado"
        )

    if (
        servicio.estetica_id
        != user["estetica_id"]
    ):

        raise HTTPException(
            status_code=403,
            detail="Sin permisos"
        )

    servicio.activo = False

    db.commit()

    return {
        "message":
            "Servicio desactivado"
    }

@router.get("/public/servicios/{slug}")
def servicios_publicos(slug: str, db: Session = Depends(get_db)):

    estetica = db.query(Estetica).filter(
        Estetica.slug == slug
    ).first()

    if not estetica:
        raise HTTPException(status_code=404, detail="No existe estética")

    servicios = (
    db.query(Servicio)
    .options(
        joinedload(Servicio.profesional)
    )
    .filter(
        Servicio.estetica_id == estetica.id,
        Servicio.activo == True
    )
    .all()
)

    return servicios