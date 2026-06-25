from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    Time,
    Boolean
)
from sqlalchemy.orm import relationship

from app.database import Base


class DisponibilidadProfesional(Base):
    __tablename__ = "disponibilidades_profesional"

    id = Column(Integer, primary_key=True)

    profesional_id = Column(
        Integer,
        ForeignKey("profesionales.id"),
        nullable=False
    )

    dia_semana = Column(
        Integer,
        nullable=False
    )

    hora_inicio = Column(
        Time,
        nullable=False
    )

    hora_fin = Column(
        Time,
        nullable=False
    )

    activo = Column(
        Boolean,
        default=True
    )

    profesional = relationship(
    "Profesional",
    back_populates="disponibilidades"
)