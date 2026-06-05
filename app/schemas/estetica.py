from pydantic import BaseModel

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


class EsteticaResponse(BaseModel):

    id: int

    nombre: str
    slug: str

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