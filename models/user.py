from sqlalchemy import Column, Integer, String, SmallInteger, DateTime
from db.session import Base


class User(Base):

    __tablename__ = "usuarios"

    # Definición de columnas según el diagrama
    id_usuario = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False) # 255 para soportar hash en el futuro
    id_rol = Column(Integer, nullable=False) # FK a la tabla de roles (que crearemos luego)
    estado = Column(SmallInteger, default=1) # 1: Activo, 0: Inactivo
    intentos_login = Column(Integer, default=0)
    hora_intento = Column(DateTime, nullable=True)