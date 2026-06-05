from pydantic import BaseModel
from datetime import date

class ClienteCreate(BaseModel):
    
    nombre_completo: str
    fecha_nacimiento: date
    telefono: str
    