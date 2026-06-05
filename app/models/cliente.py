from sqlalchemy import (
    Boolean,
    Column,
    Integer,
    String,
    Date,
    Text,
    ForeignKey
)

from sqlalchemy.orm import relationship

from app.database import Base

class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True)

    estetica_id = Column(
        Integer,
        ForeignKey("esteticas.id")
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id")
    )

    google_id = Column(String, unique=True)

    email = Column(String, unique=True)

    nombre_google = Column(String)

    foto_url = Column(Text)

    nombre_completo = Column(String)

    fecha_nacimiento = Column(Date)

    perfil_completo = Column(Boolean, default=False)

    telefono = Column(String)

    estetica = relationship(
        "Estetica",
        back_populates="clientes"
    )

    user = relationship(
        "User",
        back_populates="cliente"
    )