from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from sqlalchemy.orm import Session

from google.oauth2 import id_token
from google.auth.transport import requests
import os
import socket
import urllib3.util.connection as urllib3_connection

from dotenv import load_dotenv

from app.security import create_access_token

from app.dependencies import get_current_user

from app.database import get_db

from app.models.user import User

from app.schemas.auth import GoogleAuthRequest
from app.models.cliente import Cliente
from app.models.estetica import Estetica
from app.models.membership import Membership

router = APIRouter()

load_dotenv()

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")

# En algunas redes locales macOS resuelve Google primero por IPv6 aunque no
# tenga conectividad IPv6. Eso deja la validación del token esperando. Forzar
# IPv4 evita el bloqueo y no afecta el protocolo HTTPS.
urllib3_connection.allowed_gai_family = lambda: socket.AF_INET


@router.get("/me")
def get_me(
    user = Depends(get_current_user)
):

    return {
        "user": user
    }


@router.post("/google-login")
def google_login(
    body: GoogleAuthRequest,
    db: Session = Depends(get_db)
):

    estetica = db.query(Estetica).filter(Estetica.slug == body.slug).first()
    if not estetica:
        raise HTTPException(status_code=404, detail="Estetica no encontrada")

    try:

        google_user = id_token.verify_oauth2_token(
            body.credential,
            requests.Request(),
            GOOGLE_CLIENT_ID,
            clock_skew_in_seconds=10,
        )

        email = google_user.get("email")

        google_id = google_user.get("sub")

        nombre = google_user.get("name")

        foto = google_user.get("picture")

        if not email or not google_id:
            raise HTTPException(status_code=401, detail="La cuenta de Google no tiene identidad valida")

        email = email.lower().strip()
        user = db.query(User).filter(User.google_id == google_id).first()
        if not user:
            user = db.query(User).filter(User.email == email).first()

        if not user:

            user = User(
                email=email,
                google_id=google_id,
                nombre=nombre,
                foto_url=foto,
                role="cliente",
                # Columnas legacy; la autorizacion real vive en memberships.
                estetica_id=estetica.id
            )

            db.add(user)

            db.flush()
        else:
            if user.google_id and user.google_id != google_id:
                raise HTTPException(status_code=409, detail="El email ya usa otra identidad")
            user.google_id = google_id
            user.nombre = nombre or user.nombre
            user.foto_url = foto or user.foto_url

        membership = db.query(Membership).filter(
            Membership.user_id == user.id,
            Membership.estetica_id == estetica.id,
        ).first()
        if not membership:
            membership = Membership(
                user_id=user.id,
                estetica_id=estetica.id,
                role="cliente",
                activo=True,
            )
            db.add(membership)
        elif not membership.activo:
            raise HTTPException(status_code=403, detail="Acceso desactivado para esta estetica")

        db.commit()
        db.refresh(user)

        # 🔥 BUSCAR CLIENTE
        cliente = db.query(Cliente).filter(
            Cliente.user_id == user.id,
            Cliente.estetica_id == estetica.id,
        ).first()

        perfil_completo = False

        if cliente:
            perfil_completo = cliente.perfil_completo

        token = create_access_token({

            "sub": str(user.id),

            "role": membership.role,
            "estetica_id": estetica.id,
            "slug": estetica.slug,
        })

        return {
            "access_token": token,
            "user": {
                "id": user.id,
                "email": user.email,
                "nombre": user.nombre,
                "role": membership.role,
                "estetica_id": estetica.id,
                "slug": estetica.slug,
                "perfil_completo": perfil_completo
            }
        }

    except HTTPException:
        db.rollback()
        raise
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=401,
            detail="Google token inválido"
        )
