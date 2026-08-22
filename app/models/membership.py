from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from app.database import Base


class Membership(Base):
    """Rol de una identidad global dentro de una estetica concreta."""

    __tablename__ = "memberships"
    __table_args__ = (
        UniqueConstraint("user_id", "estetica_id", name="uq_membership_user_estetica"),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    estetica_id = Column(Integer, ForeignKey("esteticas.id", ondelete="CASCADE"), nullable=False)
    role = Column(String, nullable=False, default="cliente")
    activo = Column(Boolean, nullable=False, default=True)

    user = relationship("User", back_populates="memberships")
    estetica = relationship("Estetica", back_populates="memberships")
