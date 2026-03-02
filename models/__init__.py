"""
Database Models for EPS System
Following the ER diagram structure
"""

from datetime import datetime
from sqlalchemy import (
    Boolean,
    Column,
    Integer,
    SmallInteger,
    String,
    Date,
    DateTime,
    BigInteger,
    ForeignKey,
    Table,
    Text,
)
from sqlalchemy.orm import relationship
from db.session import Base


# Association table for many-to-many relationship between Medicos and Especialidades
medicos_especialidades = Table(
    "medicos_especialidades",
    Base.metadata,
    Column("fk_medico", Integer, ForeignKey("medicos.id_medico"), primary_key=True),
    Column(
        "fk_especialidad",
        Integer,
        ForeignKey("especialidades.id_especialidad"),
        primary_key=True,
    ),
)


class Role(Base):
    """Roles in the system (Medical, Patient, Pharmacist, Nurse, HR)"""

    __tablename__ = "roles"

    id_rol = Column(Integer, primary_key=True, index=True)
    nombre_rol = Column(String(50), unique=True, nullable=False, index=True)

    # Relationship
    usuarios = relationship("Usuario", back_populates="rol", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Role(id_rol={self.id_rol}, nombre_rol={self.nombre_rol})>"


class Usuario(Base):
    """Users table - Central user management"""

    __tablename__ = "usuarios"

    id_usuario = Column(Integer, primary_key=True, index=True)
    num_documento = Column(BigInteger, unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)
    fk_id_rol = Column("id_rol", Integer, ForeignKey("roles.id_rol"), nullable=False)
    estado = Column(SmallInteger, default=1, nullable=False)
    intentos_login = Column(SmallInteger, default=0)
    tiempo_da_fallo_login = Column("tiempo_de_fallo_login", DateTime, nullable=True)

    # Relationships
    rol = relationship("Role", back_populates="usuarios")
    medico = relationship("Medico", back_populates="usuario", uselist=False, cascade="all, delete-orphan")
    paciente = relationship("Paciente", back_populates="usuario", uselist=False, cascade="all, delete-orphan")
    enfermero = relationship("Enfermero", back_populates="usuario", uselist=False, cascade="all, delete-orphan")
    farmaceuta = relationship("Farmaceuta", back_populates="usuario", uselist=False, cascade="all, delete-orphan")
    talento_humano = relationship("TalentoHumano", back_populates="usuario", uselist=False, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Usuario(id_usuario={self.id_usuario}, num_documento={self.num_documento}, rol_id={self.fk_id_rol})>"


class Especialidad(Base):
    """Medical specialties"""

    __tablename__ = "especialidades"

    id_especialidad = Column(Integer, primary_key=True, index=True)
    nombre_especialidad = Column(String(50), nullable=False)
    requiere_remision = Column(Boolean, default=False)

    # Relationship
    medicos = relationship(
        "Medico",
        secondary=medicos_especialidades,
        back_populates="especialidades",
    )

    def __repr__(self):
        return f"<Especialidad(id_especialidad={self.id_especialidad}, nombre={self.nombre_especialidad})>"


class Medico(Base):
    """Doctors/Physicians"""

    __tablename__ = "medicos"

    id_medico = Column(Integer, primary_key=True, index=True)
    nombres = Column(String(50), nullable=False)
    apellidos = Column(String(50), nullable=False)
    num_licencia = Column(Integer, unique=True, nullable=False, index=True)
    estado = Column(String(20), default="activo", nullable=False)
    fk_id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=False, unique=True)

    # Relationships
    usuario = relationship("Usuario", back_populates="medico")
    especialidades = relationship(
        "Especialidad",
        secondary=medicos_especialidades,
        back_populates="medicos",
    )

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Medico(id_medico={self.id_medico}, nombres={self.nombres}, apellidos={self.apellidos})>"


class Paciente(Base):
    """Patients"""

    __tablename__ = "pacientes"

    id_paciente = Column(BigInteger, primary_key=True, index=True)
    nombres = Column(String(50), nullable=False)
    apellidos = Column(String(50), nullable=False)
    estado = Column(SmallInteger, default=1, nullable=False)
    consentimiento_datos = Column(Boolean, default=False)
    num_afiliacion = Column(BigInteger, unique=True, nullable=False, index=True)
    genero = Column(String(50), nullable=False)
    fecha_nac = Column(Date, nullable=False)
    direccion = Column(String(100), nullable=True)
    contacto_emergencia = Column(String(50), nullable=True)
    telefono_emergencia = Column(BigInteger, nullable=True)
    grupo_sanguineo = Column(String(2), nullable=True)
    factor_RH = Column("factor_rh", String(1), nullable=True)
    email = Column(String(80), nullable=True, index=True)
    id_recepcionista = Column(BigInteger, ForeignKey("recepcionistas.id_recepcionista"), nullable=False)
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=False, unique=True)

    # Relationship
    usuario = relationship("Usuario", back_populates="paciente")

    @property
    def num_afiliacion_formateado(self) -> str:
        raw = str(self.num_afiliacion)
        if len(raw) >= 9:
            date_part = raw[:8]
            sequence_part = str(int(raw[8:]))
            return f"EPS-{date_part}-{sequence_part}"
        return f"EPS-{raw}"

    def __repr__(self):
        return f"<Paciente(id_paciente={self.id_paciente}, nombres={self.nombres}, num_afiliacion={self.num_afiliacion})>"


class Recepcionista(Base):
    """Reception staff"""

    __tablename__ = "recepcionistas"

    id_recepcionista = Column(BigInteger, primary_key=True, index=True)
    nombres = Column(String(50), nullable=False)
    apellidos = Column(String(50), nullable=False)
    estado = Column(SmallInteger, nullable=False)
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=False)

    def __repr__(self):
        return f"<Recepcionista(id_recepcionista={self.id_recepcionista}, nombres={self.nombres})>"


class Enfermero(Base):
    """Nurses"""

    __tablename__ = "enfermeros"

    id_enfermero = Column(Integer, primary_key=True, index=True)
    nombres = Column(String(50), nullable=False)
    apellidos = Column(String(50), nullable=False)
    estado = Column(String(20), default="activo", nullable=False)
    fk_id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=False, unique=True)

    # Relationship
    usuario = relationship("Usuario", back_populates="enfermero")

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Enfermero(id_enfermero={self.id_enfermero}, nombres={self.nombres})>"


class Farmaceuta(Base):
    """Pharmacists"""

    __tablename__ = "farmaceuta"

    id_farmaceuta = Column(Integer, primary_key=True, index=True)
    nombres = Column(String(50), nullable=False)
    apellidos = Column(String(50), nullable=False)
    estado = Column(String(20), default="activo", nullable=False)
    fk_id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=False, unique=True)

    # Relationship
    usuario = relationship("Usuario", back_populates="farmaceuta")

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Farmaceuta(id_farmaceuta={self.id_farmaceuta}, nombres={self.nombres})>"


class TalentoHumano(Base):
    """Human Resources / HR Staff"""

    __tablename__ = "talento_humano"

    id_TH = Column(Integer, primary_key=True, index=True)
    nombres = Column(String(50), nullable=False)
    apellidos = Column(String(50), nullable=False)
    estado = Column(String(20), default="activo", nullable=False)
    fk_id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=False, unique=True)

    # Relationship
    usuario = relationship("Usuario", back_populates="talento_humano")

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<TalentoHumano(id_TH={self.id_TH}, nombres={self.nombres})>"
