from pydantic import BaseModel

class ProfesionalCreate(BaseModel):
    nombre: str

class ProfesionalOut(BaseModel):

    id: int

    nombre: str

    class Config:
        from_attributes = True


class ProfesionalUpdate(BaseModel):
    nombre: str        