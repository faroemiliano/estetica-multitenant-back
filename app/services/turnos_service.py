from datetime import datetime, timedelta
from app.models.turno import Turno



def validar_disponibilidad(
    db,
    estetica_id: int,
    profesional_id: int,
    hora_inicio: datetime,
    duracion: int
):

    hora_fin = hora_inicio + timedelta(minutes=duracion)

    turnos = db.query(Turno).filter(
        Turno.estetica_id == estetica_id,
        Turno.profesional_id == profesional_id
    ).all()

    for t in turnos:

        if t.hora_inicio and t.hora_fin:

            if hora_inicio < t.hora_fin and t.hora_inicio < hora_fin:
                return False

    return True