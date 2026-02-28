from sqlalchemy import Column, Integer, String, BigInteger, ForeignKey, Boolean, Date
from db.session import Base

class MEDICOS(Base):
    __tablename__ = "medicos"
    id_medico = Column(BigInteger, primary_key=True)
    nombres = Column(String(50))
    apellidos = Column(String(50))
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"))

class PACIENTES(Base):
    __tablename__ = "pacientes"
    id_paciente = Column(BigInteger, primary_key=True)
    nombres = Column(String(50))
    apellidos = Column(String(50))
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"))

class FARMACEUTA(Base):
    __tablename__ = "farmaceutas"
    id_farmaceuta = Column(BigInteger, primary_key=True)
    nombres = Column(String(50))
    apellidos = Column(String(50))
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"))

class ENFERMEROS(Base):
    __tablename__ = "enfermeros"
    id_enfermero = Column(BigInteger, primary_key=True)
    nombres = Column(String(50))
    apellidos = Column(String(50))
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"))

class TALENTO_HUMANO(Base):
    __tablename__ = "talento_humano"
    id_th = Column(BigInteger, primary_key=True)
    nombres = Column(String(50))
    apellidos = Column(String(50))
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"))

class RECEPCIONISTAS(Base):
    __tablename__ = "recepcionistas" # Tabla nueva descubierta
    id_recepcionista = Column(BigInteger, primary_key=True)
    nombres = Column(String(50))
    apellidos = Column(String(50))
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"))
