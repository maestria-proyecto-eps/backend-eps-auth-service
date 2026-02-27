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
    __tablename__ = "Farmaceuta"
    id_farmaceuta = Column(BigInteger, primary_key=True)
    nombres = Column(String(50))
    apellidos = Column(String(50))
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"))

class ENFERMEROS(Base):
    __tablename__ = "Enfermeros"
    id_enfermero = Column(BigInteger, primary_key=True)
    nombres = Column(String(50))
    apellidos = Column(String(50))
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"))

class TALENTO_HUMANO(Base):
    __tablename__ = "Talento Humano"
    id_TH = Column(BigInteger, primary_key=True)
    nombres = Column(String(50))
    apellidos = Column(String(50))
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"))

