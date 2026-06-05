from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.profesional import Profesional
from app.dependencies import get_current_user
from app.schemas.profesional import ProfesionalCreate

router = APIRouter()

def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


@router.get("/profesionales")
def obtener_profesionales(

    user = Depends(get_current_user),

    db: Session = Depends(get_db)

):

    return (
        db.query(Profesional)
        .filter(
            Profesional.estetica_id
            == user["estetica_id"]
        )
        .all()
    )

@router.post("/profesionales")
def crear_profesional(

    body: ProfesionalCreate,

    user = Depends(get_current_user),

    db: Session = Depends(get_db)

):

    profesional = Profesional(
        nombre=body.nombre,
        estetica_id=user["estetica_id"]
    )

    db.add(profesional)

    db.commit()

    db.refresh(profesional)

    return profesional

@router.put("/profesionales/{id}")
def editar_profesional(
    id: int,
    body: ProfesionalCreate,
    user = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    profesional = (
        db.query(Profesional)
        .filter(
            Profesional.id == id,
            Profesional.estetica_id == user["estetica_id"]
        )
        .first()
    )

    if not profesional:
        raise HTTPException(
            status_code=404,
            detail="Profesional no encontrado"
        )

    profesional.nombre = body.nombre

    db.commit()

    db.refresh(profesional)

    return profesional

@router.delete("/profesionales/{id}")
def eliminar_profesional(
    id: int,
    user = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    profesional = (
        db.query(Profesional)
        .filter(
            Profesional.id == id,
            Profesional.estetica_id == user["estetica_id"]
        )
        .first()
    )

    if not profesional:
        raise HTTPException(
            status_code=404,
            detail="Profesional no encontrado"
        )

    db.delete(profesional)

    db.commit()

    return {
        "message": "Profesional eliminado"
    }