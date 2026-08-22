from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.security import verify_token
from app.database import get_db
from app.models.membership import Membership
from app.models.user import User
from app.models.estetica import Estetica

security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):

    try:

        token = credentials.credentials

        payload = verify_token(token)

        user_id = int(payload["sub"])
        estetica_id = int(payload["estetica_id"])
        membership = db.query(Membership).filter(
            Membership.user_id == user_id,
            Membership.estetica_id == estetica_id,
            Membership.activo.is_(True),
        ).first()
        user = db.query(User).filter(User.id == user_id).first()
        estetica = db.query(Estetica).filter(
            Estetica.id == estetica_id,
            Estetica.activo.is_(True),
        ).first()

        if not user or not membership or not estetica:
            raise HTTPException(status_code=401, detail="Sesion sin acceso a esta estetica")

        return {
            **payload,
            "sub": str(user.id),
            "estetica_id": membership.estetica_id,
            "role": membership.role,
        }

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Token inválido"
        )


def require_admin(user=Depends(get_current_user)):
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Se requiere rol de administrador")
    return user
