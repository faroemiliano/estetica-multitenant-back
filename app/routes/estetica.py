from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.estetica import Estetica
from app.schemas.estetica import EsteticaCreate, EsteticaResponse, EsteticaUpdate
from app.dependencies import get_current_user


router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/esteticas")
def crear_estetica(
    estetica: EsteticaCreate,
    db: Session = Depends(get_db)
):

    nueva_estetica = Estetica(
        nombre=estetica.nombre,
        slug=estetica.slug,

        logo_url=estetica.logo_url,
        color_primario=estetica.color_primario,
        hero_image=estetica.hero_image,

        instagram_url=estetica.instagram_url,
        whatsapp=estetica.whatsapp,

        direccion=estetica.direccion
    )

    db.add(nueva_estetica)

    db.commit()

    db.refresh(nueva_estetica)

    return {
        "message": "Estética creada",
        "id": nueva_estetica.id
    }

@router.get("/esteticas/{slug}", response_model=EsteticaResponse)
def obtener_estetica_por_slug(
    slug: str,
    db: Session = Depends(get_db)
):
    estetica = db.query(Estetica).filter(
        Estetica.slug == slug
    ).first()

    if not estetica:
        raise HTTPException(
            status_code=404,
            detail="Estética no encontrada"
        )

    return estetica

@router.put("/esteticas/{slug}")
def actualizar_estetica(
    slug: str,
    data: EsteticaUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=403,
            detail="No autorizado"
        )
    print("Actualizando estética:", slug, data)
    estetica = db.query(Estetica).filter(
        Estetica.slug == slug
    ).first()

    if not estetica:
        raise HTTPException(
            status_code=404,
            detail="Estética no encontrada"
        )

    updates = data.dict(exclude_unset=True)

    for key, value in updates.items():
        setattr(estetica, key, value)

    db.commit()
    db.refresh(estetica)

    return estetica