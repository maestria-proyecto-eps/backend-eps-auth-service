from sqlalchemy import Column, Integer, String, SmallInteger, TIMESTAMP, BigInteger
from db.session import Base


class USUARIOS(Base):

    __tablename__ = "usuarios"

    # Definición de columnas según el diagrama
    id_usuario = Column(Integer, primary_key=True, index=True, autoincrement=True)
    num_documento = Column(BigInteger, unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False) # 255 para soportar hash en el futuro
    id_rol = Column(Integer, nullable=False) # FK a la tabla de roles (que crearemos luego)
    estado = Column(SmallInteger, default=1) # 1: Activo, 0: Inactivo
    intentos_login = Column(Integer, default=0)
    tiempo_de_fallo_login = Column(TIMESTAMP, nullable=True)

class ROLES(Base):
    __tablename__ = "roles"

    id_rol = Column(Integer, primary_key=True, index=True)
    nombre_rol = Column(String(50), nullable=False, unique=True)