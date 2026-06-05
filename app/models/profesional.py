from sqlalchemy import Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from app.database import Base

class Profesional(Base):
    __tablename__ = "profesionales"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    descripcion = Column(Text, nullable=True)
    foto = Column(String, nullable=True)
    estetica_id = Column(
        Integer,
        ForeignKey("esteticas.id")
    )

    servicios = relationship(
        "Servicio",
        back_populates="profesional"
    )