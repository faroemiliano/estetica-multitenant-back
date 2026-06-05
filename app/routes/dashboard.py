from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import date, datetime, time

from app.database import SessionLocal
from app.dependencies import get_current_user
from app.models.turno import Turno

router = APIRouter()


def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


@router.get("/dashboard/stats")
def dashboard_stats(
    user = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    hoy = date.today()

    inicio_dia = datetime.combine(hoy, time.min)
    fin_dia = datetime.combine(hoy, time.max)

    turnos_hoy = db.query(Turno).filter(
        Turno.estetica_id == user["estetica_id"],
        Turno.hora_inicio >= inicio_dia,
        Turno.hora_inicio <= fin_dia
    ).count()

    pendientes = db.query(Turno).filter(
        Turno.estetica_id == user["estetica_id"],
        Turno.estado == "pendiente"
    ).count()

    confirmados = db.query(Turno).filter(
        Turno.estetica_id == user["estetica_id"],
        Turno.estado == "confirmado"
    ).count()

    cancelados = db.query(Turno).filter(
        Turno.estetica_id == user["estetica_id"],
        Turno.estado == "cancelado"
    ).count()

    finalizados = db.query(Turno).filter(
        Turno.estetica_id == user["estetica_id"],
        Turno.estado == "finalizado"
    ).count()

    return {
        "turnos_hoy": turnos_hoy,
        "pendientes": pendientes,
        "confirmados": confirmados,
        "cancelados": cancelados,
        "finalizados": finalizados
    }