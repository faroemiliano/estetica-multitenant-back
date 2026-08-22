from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.profesional import Profesional
from app.dependencies import get_current_user, require_admin
from app.schemas.profesional import ProfesionalCreate, ProfesionalUpdate
from app.models.disponibilidadProfesional import DisponibilidadProfesional

router = APIRouter()

@router.get("/profesionales")
def obtener_profesionales(

    user = Depends(require_admin),

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

    user = Depends(require_admin),

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
    body: ProfesionalUpdate,
    user = Depends(require_admin),
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
    user = Depends(require_admin),
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

@router.get("/profesionales/{profesional_id}/disponibilidad")
def obtener_disponibilidad(
    profesional_id: int,
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):

    profesional = db.query(Profesional).filter(
        Profesional.id == profesional_id,
        Profesional.estetica_id == user["estetica_id"],
    ).first()
    if not profesional:
        raise HTTPException(status_code=404, detail="Profesional no encontrado")

    disponibilidades = db.query(
        DisponibilidadProfesional
    ).filter(
        DisponibilidadProfesional.profesional_id == profesional_id
    ).all()

    return disponibilidades

@router.put("/profesionales/{profesional_id}/disponibilidad")
def guardar_disponibilidad(
    profesional_id: int,
    body: list[dict],
    user=Depends(require_admin),
    db: Session = Depends(get_db)
):

    profesional = db.query(Profesional).filter(
        Profesional.id == profesional_id,
        Profesional.estetica_id == user["estetica_id"],
    ).first()
    if not profesional:
        raise HTTPException(status_code=404, detail="Profesional no encontrado")

    db.query(
        DisponibilidadProfesional
    ).filter(
        DisponibilidadProfesional.profesional_id == profesional_id
    ).delete()

    for item in body:

        nueva = DisponibilidadProfesional(
            profesional_id=profesional_id,
            dia_semana=item["dia_semana"],
            hora_inicio=item["hora_inicio"],
            hora_fin=item["hora_fin"],
            activo=item["activo"]
        )

        db.add(nueva)

    db.commit()

    return {"ok": True}
