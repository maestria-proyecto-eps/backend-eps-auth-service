from sqlalchemy import Column, Integer, String, BigInteger, ForeignKey, Boolean, Date
from sqlalchemy.orm import declarative_base

ProfilesBase = declarative_base()

class MEDICOS(ProfilesBase):
    __tablename__ = "medicos"
    id_medico = Column(BigInteger, primary_key=True)
    nombres = Column(String(50))
    apellidos = Column(String(50))
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"))

class PACIENTES(ProfilesBase):
    __tablename__ = "pacientes"
    id_paciente = Column(BigInteger, primary_key=True)
    nombres = Column(String(50))
    apellidos = Column(String(50))
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"))

class FARMACEUTA(ProfilesBase):
    __tablename__ = "farmaceutas"
    id_farmaceuta = Column(BigInteger, primary_key=True)
    nombres = Column(String(50))
    apellidos = Column(String(50))
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"))

class ENFERMEROS(ProfilesBase):
    __tablename__ = "enfermeros"
    id_enfermero = Column(BigInteger, primary_key=True)
    nombres = Column(String(50))
    apellidos = Column(String(50))
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"))

class TALENTO_HUMANO(ProfilesBase):
    __tablename__ = "talento_humano"
    id_th = Column(BigInteger, primary_key=True)
    nombres = Column(String(50))
    apellidos = Column(String(50))
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"))

class RECEPCIONISTAS(ProfilesBase):
    __tablename__ = "recepcionistas" # Tabla nueva descubierta
    id_recepcionista = Column(BigInteger, primary_key=True)
    nombres = Column(String(50))
    apellidos = Column(String(50))
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"))
