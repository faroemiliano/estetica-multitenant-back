from pydantic import BaseModel
from app.schemas.profesional import ProfesionalOut
class ServicioCreate(BaseModel):

   

    nombre: str

    descripcion: str

    duracion: int

    precio: float

    profesional_id: int | None = None



class ServicioUpdate(BaseModel):

    nombre: str

    descripcion: str

    duracion: int

    precio: float

    profesional_id: int | None = None

class ServicioOut(BaseModel):

    id: int

    nombre: str

    descripcion: str

    duracion: int

    precio: float

    profesional_id: int | None = None

    profesional: ProfesionalOut | None = None

    class Config:
        from_attributes = True