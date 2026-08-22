from pydantic import BaseModel
from pydantic import Field

class EsteticaCreate(BaseModel):
    nombre: str
    slug: str

    logo_url: str | None = None
    color_primario: str | None = None
    hero_image: str | None = None
    instagram_url: str | None = None
    whatsapp: str | None = None

    direccion: str | None = None

    horarios: str | None = None


class EsteticaProvision(EsteticaCreate):
    admin_email: str
    admin_nombre: str | None = None
    slug: str = Field(pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$", min_length=2, max_length=80)


class EsteticaResponse(BaseModel):

    id: int

    nombre: str
    slug: str
    activo: bool = True

    logo_url: str | None = None
    color_primario: str | None = None

    hero_image: str | None = None
    instagram_url: str | None = None

    whatsapp: str | None = None
    direccion: str | None = None

    horarios: str | None = None

    class Config:
        from_attributes = True


class EsteticaUpdate(BaseModel):
    logo_url: str | None = None
    hero_image: str | None = None

    whatsapp: str | None = None
    instagram_url: str | None = None

    direccion: str | None = None

    horarios: str | None = None


class EsteticaEstadoUpdate(BaseModel):
    activo: bool
