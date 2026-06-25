from datetime import datetime, timedelta
import json

from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.orm import Session, joinedload

from app.database import SessionLocal

from app.models.turno import Turno

from app.schemas.turno import TurnoCreate, TurnoOut

from app.dependencies import get_current_user

from app.models.estetica import Estetica
from app.models.servicio import Servicio
from app.services.turnos_service import validar_disponibilidad
from app.models.disponibilidadProfesional import DisponibilidadProfesional

router = APIRouter()


def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


@router.post("/turnos")
def crear_turno(
    body: TurnoCreate,
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):

    servicio = db.query(Servicio).filter(
        Servicio.id == body.servicio_id
    ).first()

    if not servicio:
        raise HTTPException(404, "Servicio no encontrado")

    hora_inicio = datetime.strptime(
        f"{body.fecha} {body.hora}",
        "%Y-%m-%d %H:%M"
    )

    if hora_inicio <= datetime.now():
        raise HTTPException(
            400,
            "No se puede reservar un horario pasado"
        )

    ok = validar_disponibilidad(
        db=db,
        estetica_id=user["estetica_id"],
        profesional_id=servicio.profesional_id,
        hora_inicio=hora_inicio,
        duracion=servicio.duracion
    )

    if not ok:
        raise HTTPException(
            400,
            "Ese profesional ya tiene turno en ese horario"
        )

    hora_fin = hora_inicio + timedelta(minutes=servicio.duracion)

    turno = Turno(
        cliente_id=int(user["sub"]),
        servicio_id=body.servicio_id,
        profesional_id=servicio.profesional_id,
        estetica_id=user["estetica_id"],
        hora_inicio=hora_inicio,
        hora_fin=hora_fin
    )

    db.add(turno)
    db.commit()
    db.refresh(turno)

    return turno

@router.get("/turnos", response_model=list[TurnoOut])
def obtener_turnos(
    user = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    turnos = db.query(Turno).options(
        joinedload(Turno.servicio),
        joinedload(Turno.cliente)
    ).filter(
        Turno.estetica_id == user["estetica_id"]
    ).order_by(
        Turno.hora_inicio
    ).all()

    return turnos

# @router.get("/horarios-disponibles")
# def horarios_disponibles(
#     fecha: str,
#     profesional_id: int,
#     user=Depends(get_current_user),
#     db: Session = Depends(get_db)
# ):

#     estetica = db.query(Estetica).filter(
#         Estetica.id == user["estetica_id"]
#     ).first()

#     if not estetica:
#         raise HTTPException(404, "Estética no encontrada")

#     from datetime import datetime, timedelta

#     intervalo = timedelta(minutes=estetica.intervalo_turnos)

#     fecha_obj = datetime.strptime(
#         fecha,
#         "%Y-%m-%d"
#     )

#     dia_semana = fecha_obj.weekday()

#     disponibilidad = db.query(
#         DisponibilidadProfesional
#     ).filter(
#         DisponibilidadProfesional.profesional_id == profesional_id,
#         DisponibilidadProfesional.dia_semana == dia_semana,
#         DisponibilidadProfesional.activo == True
#     ).first()

#     if not disponibilidad:
#         return []

#     bloques = [{
#         "inicio": disponibilidad.hora_inicio.strftime("%H:%M"),
#         "fin": disponibilidad.hora_fin.strftime("%H:%M")
#     }]

#     # turnos del día
#     inicio_dia = datetime.strptime(
#     fecha,
#     "%Y-%m-%d"
# )

#     fin_dia = inicio_dia + timedelta(days=1)

#     turnos = db.query(Turno).filter(
#         Turno.estetica_id == user["estetica_id"],
#         Turno.profesional_id == profesional_id,
#         Turno.hora_inicio >= inicio_dia,
#         Turno.hora_inicio < fin_dia,
#         Turno.estado != "cancelado"
#     ).all()

#     ocupados = [(t.hora_inicio, t.hora_fin) for t in turnos]

#     def solapa(a_inicio, a_fin, b_inicio, b_fin):
#         return a_inicio < b_fin and b_inicio < a_fin

#     horarios = []

#     for b in bloques:

#         inicio = datetime.strptime(f"{fecha} {b['inicio']}", "%Y-%m-%d %H:%M")
#         fin = datetime.strptime(f"{fecha} {b['fin']}", "%Y-%m-%d %H:%M")

#         actual = inicio

#         while actual + intervalo <= fin:

#             slot_inicio = actual
#             slot_fin = actual + intervalo

#             if not any(
#                 solapa(slot_inicio, slot_fin, o[0], o[1])
#                 for o in ocupados
#             ):
#                 horarios.append(actual.strftime("%H:%M"))

#             actual += intervalo

#     return horarios


@router.get("/mis-turnos", response_model=list[TurnoOut])
def obtener_mis_turnos(
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):

    turnos = db.query(Turno).options(
        joinedload(Turno.servicio),
        joinedload(Turno.profesional)
    ).filter(
        Turno.cliente_id == int(user["sub"]),
        Turno.visible_cliente == True
    ).order_by(
        Turno.hora_inicio
    ).all()

    return turnos

@router.delete("/mis-turnos/{id}")
def ocultar_turno(
    id: int,
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    turno = db.query(Turno).filter(
        Turno.id == id,
        Turno.cliente_id == int(user["sub"])
    ).first()

    if not turno:
        raise HTTPException(404, "Turno no encontrado")

    turno.visible_cliente = False

    db.commit()

    return {"ok": True}

@router.put("/turnos/{id}/estado")
def cambiar_estado_turno(


    id: int,

    estado: str,

    user = Depends(get_current_user),

    db: Session = Depends(get_db)
):

    turno = db.query(Turno).filter(
        Turno.id == id
    ).first()

    if not turno:

        raise HTTPException(
            status_code=404,
            detail="Turno no encontrado"
        )

    # ADMIN puede todo
    if user["role"] == "admin":

        if (
            turno.estetica_id
            != user["estetica_id"]
        ):

            raise HTTPException(
                status_code=403,
                detail="Sin permisos"
            )

    # CLIENTE solo cancelar SU turno
    else:

        if (
            estado != "cancelado"
            or turno.cliente_id != int(user["sub"])
        ):

            raise HTTPException(
                status_code=403,
                detail="Sin permisos"
            )

    turno.estado = estado

    db.commit()

    db.refresh(turno)

    return turno


@router.get("/estetica/horarios")
def obtener_horarios(
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    estetica = db.query(Estetica).filter(
        Estetica.id == user["estetica_id"]
    ).first()

    return {
        "horarios": json.loads(estetica.horarios or "[]")
    }

@router.put("/estetica/horarios")
def actualizar_horarios(
    body: dict,
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):

    if user["role"] != "admin":
        raise HTTPException(403, "No autorizado")

    estetica = db.query(Estetica).filter(
        Estetica.id == user["estetica_id"]
    ).first()

    estetica.horarios = json.dumps(body["horarios"])

    db.commit()

    return {"ok": True}

@router.get("/mis-turnos-archivados", response_model=list[TurnoOut])
def obtener_turnos_archivados(
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return (
        db.query(Turno)
        .options(
            joinedload(Turno.servicio),
            joinedload(Turno.profesional)
        )
        .filter(
            Turno.cliente_id == int(user["sub"]),
            Turno.visible_cliente == False
        )
        .order_by(Turno.hora_inicio.desc())
        .all()
    )

@router.put("/turnos/{id}/mostrar")
def mostrar_turno(
    id: int,
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    turno = db.query(Turno).filter(
        Turno.id == id,
        Turno.cliente_id == int(user["sub"])
    ).first()

    if not turno:
        raise HTTPException(404, "Turno no encontrado")

    turno.visible_cliente = True

    db.commit()

    return {"ok": True}

@router.get("/horarios-disponibles")
def horarios_disponibles(
    profesional_id: int,
    fecha: str,
    servicio_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):

    servicio = db.query(Servicio).filter(
        Servicio.id == servicio_id
    ).first()

    if not servicio:
        raise HTTPException(404, "Servicio no encontrado")

    duracion = servicio.duracion

    dia_inicio = datetime.strptime(
        fecha + " 00:00",
        "%Y-%m-%d %H:%M"
    )

    dia_fin = datetime.strptime(
        fecha + " 23:59",
        "%Y-%m-%d %H:%M"
    )

    turnos = db.query(Turno).filter(
        Turno.profesional_id == profesional_id,
        Turno.hora_inicio >= dia_inicio,
        Turno.hora_inicio <= dia_fin,
        Turno.estado != "cancelado"
    ).all()

    numero_dia = dia_inicio.weekday()

    disponibilidades = db.query(
        DisponibilidadProfesional
    ).filter(
        DisponibilidadProfesional.profesional_id == profesional_id,
        DisponibilidadProfesional.dia_semana == numero_dia,
        DisponibilidadProfesional.activo == True
    ).all()

    horarios_libres = []

    ahora = datetime.now()

    for disp in disponibilidades:

        inicio_jornada = datetime.combine(
            dia_inicio.date(),
            disp.hora_inicio
        )

        fin_jornada = datetime.combine(
            dia_inicio.date(),
            disp.hora_fin
        )

        actual = inicio_jornada

        while actual + timedelta(minutes=duracion) <= fin_jornada:

            posible_fin = actual + timedelta(
                minutes=duracion
            )

            # Si el horario ya pasó, no mostrarlo
            if actual <= ahora:
                actual += timedelta(minutes=15)
                continue

            ocupado = False

            for turno in turnos:

                if (
                    actual < turno.hora_fin
                    and posible_fin > turno.hora_inicio
                ):
                    ocupado = True
                    break

            if not ocupado:
                horarios_libres.append(
                    actual.strftime("%H:%M")
                )

            actual += timedelta(minutes=15)

    return horarios_libres