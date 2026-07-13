from pydantic import BaseModel
from app.schemas.profesional import ProfesionalOut


class ServicioCreate(BaseModel):

    nombre: str

    descripcion: str

    duracion: int

    categoria: str | None = None

    precio: float

    profesional_id: int | None = None

    requiere_whatsapp: bool = False


class ServicioUpdate(BaseModel):

    nombre: str

    descripcion: str

    duracion: int

    categoria: str | None = None

    precio: float

    profesional_id: int | None = None

    requiere_whatsapp: bool = False


class ServicioOut(BaseModel):

    id: int

    nombre: str

    descripcion: str

    duracion: int

    categoria: str | None = None

    precio: float

    profesional_id: int | None = None

    requiere_whatsapp: bool = False

    profesional: ProfesionalOut | None = None

    class Config:
        from_attributes = True