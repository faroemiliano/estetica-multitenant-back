from sqlalchemy import create_engine

from sqlalchemy.orm import declarative_base

from sqlalchemy.orm import sessionmaker

from dotenv import load_dotenv

import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


from app.models.user import User
from app.models.cliente import Cliente
from app.models.estetica import Estetica
from app.models.servicio import Servicio
from app.models.turno import Turno
from app.models.profesional import Profesional