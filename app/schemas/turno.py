from datetime import datetime
from pydantic import BaseModel

from app.schemas.servicio import ServicioOut
from app.schemas.user import UserSimple
from app.schemas.profesional import ProfesionalOut


class TurnoCreate(BaseModel):

    servicio_id: int

    fecha: str

    hora: str

    


class TurnoOut(BaseModel):

    id: int

    cliente_id: int

    servicio_id: int

    estetica_id: int

    profesional_id: int

    hora_inicio: datetime
    
    hora_fin: datetime  

    estado: str

    servicio: ServicioOut | None = None

    profesional: ProfesionalOut | None = None

    cliente: UserSimple

    class Config:

        from_attributes = True