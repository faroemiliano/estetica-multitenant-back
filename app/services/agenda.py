from datetime import datetime, timedelta

def generar_slots(inicio: datetime, fin: datetime, intervalo: timedelta):
    slots = []
    actual = inicio

    while actual + intervalo <= fin:
        slots.append(actual)
        actual += intervalo

    return slots


def esta_ocupado(slot_inicio: datetime, slot_fin: datetime, ocupados: list[tuple[datetime, datetime]]):
    return any(
        slot_inicio < o_fin and o_inicio < slot_fin
        for o_inicio, o_fin in ocupados
    )