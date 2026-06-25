from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    ForeignKey,
    Boolean
)
from sqlalchemy.orm import relationship
from app.database import Base

class Servicio(Base):

    __tablename__ = "servicios"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    estetica_id = Column(
        Integer,
        ForeignKey("esteticas.id")
    )

    profesional_id = Column(
        Integer,
        ForeignKey("profesionales.id"),
        nullable=True
    )

    nombre = Column(
        String,
        nullable=False
    )

    categoria = Column(
    String,
    nullable=True
)

    descripcion = Column(
        String
    )

    duracion = Column(
        Integer,
        nullable=False
    )

    precio = Column(
        Float,
        nullable=False
    )

    activo = Column(
        Boolean,
        default=True
    )

    profesional = relationship(
    "Profesional",
    back_populates="servicios"
)