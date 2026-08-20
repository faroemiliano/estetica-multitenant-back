from pydantic import BaseModel
from datetime import date
from typing import Optional

class ClienteCreate(BaseModel):

    nombre_completo: str
    fecha_nacimiento: date
    telefono: str


class ClienteAdminCreate(BaseModel):
    nombre_completo: str
    email: Optional[str] = None
    fecha_nacimiento: Optional[date] = None
    telefono: str
