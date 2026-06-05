from sqlalchemy import Column, Integer, String, ForeignKey, DateTime

from app.database import Base

from datetime import datetime

from app.models.user import User

from app.models.servicio import Servicio

from sqlalchemy.orm import relationship

class Turno(Base):

    __tablename__ = "turnos"

    id = Column(Integer, primary_key=True, index=True)

    cliente_id = Column(
        Integer,
        ForeignKey("users.id")
    )

    servicio_id = Column(
        Integer,
        ForeignKey("servicios.id")
    )

    estetica_id = Column(
        Integer,
        ForeignKey("esteticas.id")
    )

    profesional_id = Column(
        Integer,
        ForeignKey("profesionales.id")
    )

    hora_inicio = Column(DateTime)   

    hora_fin = Column(DateTime)      

    estado = Column(
        String,
        default="pendiente"
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    servicio = relationship("Servicio")

    cliente = relationship("User")
    