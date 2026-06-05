from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from sqlalchemy.orm import Session

from google.oauth2 import id_token
from google.auth.transport import requests

from app.security import create_access_token

from app.dependencies import get_current_user

from app.database import SessionLocal

from app.models.user import User

from app.schemas.auth import GoogleAuthRequest
from app.models.cliente import Cliente

router = APIRouter()


def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


@router.post("/login-test")
def login_test():

    token = create_access_token({
        "sub": "1",
        "role": "admin"
    })

    return {
        "access_token": token
    }


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

    try:

        google_user = id_token.verify_oauth2_token(
            body.credential,
            requests.Request()
        )

        email = google_user.get("email")

        google_id = google_user.get("sub")

        nombre = google_user.get("name")

        foto = google_user.get("picture")

        user = db.query(User).filter(
            User.email == email
        ).first()

        if not user:

            user = User(
                email=email,
                google_id=google_id,
                nombre=nombre,
                foto_url=foto,
                role="cliente",
                estetica_id=1
            )

            db.add(user)

            db.commit()

            db.refresh(user)

        # 🔥 BUSCAR CLIENTE
        cliente = db.query(Cliente).filter(
            Cliente.user_id == user.id
        ).first()

        perfil_completo = False

        if cliente:
            perfil_completo = cliente.perfil_completo

        token = create_access_token({

            "sub": str(user.id),

            "role": user.role,

            "estetica_id":
                user.estetica_id
        })

        return {
            "access_token": token,
            "user": {
                "id": user.id,
                "email": user.email,
                "nombre": user.nombre,
                "role": user.role,
                "perfil_completo": perfil_completo
            }
        }

    except Exception as e:

        print(e)

        raise HTTPException(
            status_code=401,
            detail="Google token inválido"
        )