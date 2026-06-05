from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey
)

from sqlalchemy.orm import relationship

from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    estetica_id = Column(
        Integer,
        ForeignKey("esteticas.id")
    )

    google_id = Column(
        String,
        unique=True
    )

    email = Column(
        String,
        unique=True
    )

    nombre = Column(String)

    foto_url = Column(String)

    role = Column(
        String,
        default="cliente"
    )

    estetica = relationship("Estetica")

    cliente = relationship(
        "Cliente",
        back_populates="user",
        uselist=False
    )