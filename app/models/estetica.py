from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, Time
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base

class Estetica(Base):
    __tablename__ = "esteticas"

    id = Column(Integer, primary_key=True, index=True)

    nombre = Column(String, nullable=False)

    slug = Column(String, unique=True, nullable=False)

    logo_url = Column(Text)

    color_primario = Column(String)

    hero_image = Column(Text)

    instagram_url = Column(String)

    whatsapp = Column(String)

    horarios = Column(Text)

    hora_apertura = Column(Time, nullable=True)

    hora_cierre = Column(Time, nullable=True)
    
    intervalo_turnos = Column(Integer, default=30)

    duracion_turnos = Column(Integer)

    horarios = Column(Text)

    direccion = Column(String)

    created_at = Column(
        TIMESTAMP,
        server_default=func.now()
    )

    clientes = relationship(
    "Cliente",
    back_populates="estetica"
)