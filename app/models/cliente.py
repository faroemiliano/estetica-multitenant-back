from sqlalchemy import (
    Boolean,
    Column,
    Integer,
    String,
    Date,
    Text,
    ForeignKey,
    UniqueConstraint,
)

from sqlalchemy.orm import relationship

from app.database import Base

class Cliente(Base):
    __tablename__ = "clientes"
    __table_args__ = (
        UniqueConstraint("user_id", "estetica_id", name="uq_cliente_user_estetica"),
        UniqueConstraint("email", "estetica_id", name="uq_cliente_email_estetica"),
    )

    id = Column(Integer, primary_key=True, index=True)

    estetica_id = Column(
        Integer,
        ForeignKey("esteticas.id")
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id")
    )

    google_id = Column(String)

    email = Column(String)

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
        back_populates="clientes"
    )
