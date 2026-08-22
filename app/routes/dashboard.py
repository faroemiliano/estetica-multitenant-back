from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import date, datetime, time

from app.database import get_db
from app.dependencies import require_admin
from app.models.turno import Turno

router = APIRouter()


@router.get("/dashboard/stats")
def dashboard_stats(
    user = Depends(require_admin),
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
