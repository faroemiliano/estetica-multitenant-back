import os
import secrets

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.estetica import Estetica
from app.models.membership import Membership
from app.models.user import User
from app.schemas.estetica import EsteticaProvision, EsteticaResponse, EsteticaUpdate
from app.dependencies import require_admin


router = APIRouter()

@router.post("/admin/esteticas/provision")
def crear_estetica(
    estetica: EsteticaProvision,
    provisioning_key: str | None = Header(default=None, alias="X-Provisioning-Key"),
    db: Session = Depends(get_db)
):
    expected_key = os.getenv("PROVISIONING_KEY")
    if not expected_key:
        raise HTTPException(status_code=503, detail="Alta de esteticas no configurada")
    if not provisioning_key or not secrets.compare_digest(provisioning_key, expected_key):
        raise HTTPException(status_code=403, detail="Clave de aprovisionamiento invalida")

    if "@" not in estetica.admin_email or "." not in estetica.admin_email.rsplit("@", 1)[-1]:
        raise HTTPException(status_code=422, detail="Email de administrador invalido")

    if db.query(Estetica).filter(Estetica.slug == estetica.slug).first():
        raise HTTPException(status_code=409, detail="El slug ya esta en uso")

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

    try:
        db.add(nueva_estetica)
        db.flush()
        email = str(estetica.admin_email).lower().strip()
        admin = db.query(User).filter(User.email == email).first()
        if not admin:
            admin = User(
                email=email,
                nombre=estetica.admin_nombre or email.split("@", 1)[0],
                role="cliente",
                estetica_id=nueva_estetica.id,
            )
            db.add(admin)
            db.flush()
        membership = db.query(Membership).filter(
            Membership.user_id == admin.id,
            Membership.estetica_id == nueva_estetica.id,
        ).first()
        if not membership:
            db.add(Membership(
                user_id=admin.id,
                estetica_id=nueva_estetica.id,
                role="admin",
                activo=True,
            ))
        db.commit()
        db.refresh(nueva_estetica)
    except Exception:
        db.rollback()
        raise

    return {
        "message": "Estética creada",
        "id": nueva_estetica.id,
        "slug": nueva_estetica.slug,
        "admin_email": email,
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
    current_user = Depends(require_admin)
):
    estetica = db.query(Estetica).filter(
        Estetica.slug == slug,
        Estetica.id == current_user["estetica_id"],
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
