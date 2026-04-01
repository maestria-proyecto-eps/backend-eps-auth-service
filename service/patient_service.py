"""
Patient Service - Business logic for patient management
Handles creation, validation, and updates for patients
"""

from datetime import UTC, datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func, text
from fastapi import HTTPException, status
from core.security import Security

from models import Usuario, Paciente, Persona, Role
from schemas.patients import PacienteCreate, AffiliationStatusUpdate


class PatientService:
    """Service class for patient operations"""

    STATUS_TO_DB = {"Activo": 1, "Inactivo": 0, "Suspendido": 2}
    DB_TO_STATUS = {1: "Activo", 0: "Inactivo", 2: "Suspendido"}
    
    @staticmethod
    def generate_affiliation_number(db: Session) -> int:
        """
        Generate unique affiliation number
        Logical format: EPS-YYYYMMDD-#
        Stored in DB as integer YYYYMMDD#
        """
        today = datetime.now(UTC)
        date_prefix = today.strftime("%Y%m%d")
        prefix_as_int = int(date_prefix)

        max_today = (
            db.query(func.max(Paciente.num_afiliacion))
            .filter(
                Paciente.num_afiliacion >= prefix_as_int * 10,
                Paciente.num_afiliacion < (prefix_as_int + 1) * (10 ** 8),
            )
            .scalar()
        )

        sequence = int(str(max_today)[8:]) + 1 if max_today else 1

        return int(f"{date_prefix}{sequence}")
    
    @staticmethod
    def validate_document_unique(db: Session, num_documento: int) -> bool:
        """Check if document number already exists"""
        existing = db.query(Persona).filter(Persona.num_documento == num_documento).first()
        return existing is None
    
    @staticmethod
    def validate_email_unique(db: Session, email: str) -> bool:
        """Check if email already exists"""
        existing = db.query(Paciente).filter(Paciente.email == email).first()
        return existing is None

    @staticmethod
    def status_to_string(db_status: int | None) -> str:
        return PatientService.DB_TO_STATUS.get(db_status, "Activo")
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using project security helper."""
        return Security.get_pwd_hash(password)
    
    @staticmethod
    def create_patient(db: Session, patient_data: PacienteCreate) -> Paciente:
        """
        Create a new patient with associated usuario record
        Validates uniqueness and consent requirements
        """
        
        # Validate document uniqueness
        if not PatientService.validate_document_unique(db, patient_data.num_documento):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Document number {patient_data.num_documento} already registered"
            )
        
        # Validate email uniqueness
        if not PatientService.validate_email_unique(db, patient_data.email):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Email {patient_data.email} already registered"
            )
        
        # Validate consent
        if not patient_data.consentimiento_datos:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Data consent (Ley 1581/2012) is mandatory for patient affiliation"
            )
        
        try:
            if db.bind is not None and db.bind.dialect.name == "postgresql":
                db.execute(text("""
                    SELECT setval(
                        pg_get_serial_sequence('usuarios', 'id_usuario'),
                        COALESCE((SELECT MAX(id_usuario) FROM usuarios), 1),
                        true
                    )
                """))

            # Get 'paciente' role
            rol_paciente = db.query(Role).filter(
                func.lower(Role.nombre_rol) == 'paciente'
            ).first()
            
            if not rol_paciente:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Paciente role not configured in system"
                )
            
            persona = Persona(
                num_documento=patient_data.num_documento,
                nombres=patient_data.nombres,
                apellidos=patient_data.apellidos,
            )
            db.add(persona)
            db.flush()

            # Create usuario
            usuario = Usuario(
                num_documento=patient_data.num_documento,
                password=PatientService.hash_password(patient_data.password),
                fk_id_rol=rol_paciente.id_rol,
                estado=PatientService.STATUS_TO_DB["Activo"],
                intentos_login=0,
            )

            db.add(usuario)
            db.flush()  # Get ID without committing
            
            # Generate affiliation number
            num_afiliacion = PatientService.generate_affiliation_number(db)
            
            rol_recepcionista = db.query(Role).filter(func.lower(Role.nombre_rol) == "recepcionista").first()
            recepcionista_id = None
            if rol_recepcionista:
                recepcionista_id = (
                    db.query(Usuario.num_documento)
                    .filter(Usuario.fk_id_rol == rol_recepcionista.id_rol)
                    .order_by(Usuario.id_usuario)
                    .scalar()
                )

            if recepcionista_id is None:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="No receptionist available to register patient"
                )

            # Create paciente
            paciente = Paciente(
                id_paciente=patient_data.num_documento,
                consentimiento_datos=patient_data.consentimiento_datos,
                fecha_nac=patient_data.fecha_nacimiento,
                num_afiliacion=num_afiliacion,
                genero=patient_data.genero,
                direccion=patient_data.direccion,
                contacto_emergencia=patient_data.contacto_emergencia,
                telefono_emergencia=patient_data.telefono,
                grupo_sanguineo=patient_data.tipo_sangre,
                factor_RH=patient_data.tipo_sangre[-1],
                email=patient_data.email,
                id_recepcionista=recepcionista_id,
            )
            
            db.add(paciente)
            db.commit()
            db.refresh(paciente)
            
            return paciente
            
        except IntegrityError as e:
            db.rollback()
            import traceback
            error_detail = str(e.orig) if hasattr(e, 'orig') else str(e)
            print(f"IntegrityError: {error_detail}")
            traceback.print_exc()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Duplicate or invalid data: {error_detail}"
            )
        except Exception as e:
            db.rollback()
            import traceback
            error_trace = traceback.format_exc()
            print(f"FULL ERROR:\n{error_trace}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error creating patient: {str(e)[:200]} - {type(e).__name__}"
            )
    
    @staticmethod
    def get_patients(
        db: Session,
        skip: int = 0,
        limit: int = 10,
        estado: str = None,
        genero: str = None,
        tipo_sangre: str = None
    ) -> tuple[list[Paciente], int]:
        """
        Get all patients with optional filters
        Returns: (patients list, total count)
        """
        query = db.query(Paciente).join(Usuario, Usuario.num_documento == Paciente.id_paciente)
        
        if estado:
            status_value = PatientService.STATUS_TO_DB.get(estado.strip().title())
            if status_value is not None:
                query = query.filter(Usuario.estado == status_value)
        
        if genero:
            query = query.filter(Paciente.genero == genero)
        
        if tipo_sangre:
            query = query.filter(Paciente.grupo_sanguineo == tipo_sangre)
        
        total = query.count()
        patients = query.offset(skip).limit(limit).all()
        
        return patients, total
    
    @staticmethod
    def get_patient_by_id(db: Session, patient_id: int) -> Paciente:
        """Get patient by ID"""
        paciente = db.query(Paciente).filter(
            Paciente.id_paciente == patient_id
        ).first()
        
        if not paciente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Patient with ID {patient_id} not found"
            )
        
        return paciente
    
    @staticmethod
    def get_patient_by_user_id(db: Session, user_id: int) -> Paciente:
        """Get patient by associated user ID"""
        usuario = db.query(Usuario).filter(Usuario.id_usuario == user_id).first()
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        paciente = db.query(Paciente).filter(Paciente.id_paciente == usuario.num_documento).first()
        
        if not paciente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient profile not found for this user"
            )
        
        return paciente
    
    @staticmethod
    def update_affiliation_status(
        db: Session,
        patient_id: int,
        status_update: AffiliationStatusUpdate
    ) -> Paciente:
        """Update patient affiliation status"""
        
        paciente = PatientService.get_patient_by_id(db, patient_id)
        usuario = db.query(Usuario).filter(Usuario.num_documento == paciente.id_paciente).first()

        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User linked to patient not found",
            )

        usuario.estado = PatientService.STATUS_TO_DB[status_update.estado]

        db.commit()
        db.refresh(paciente)
        
        return paciente
    
    @staticmethod
    def update_patient_profile(
        db: Session,
        patient_id: int,
        update_data: dict
    ) -> Paciente:
        """Update patient profile information"""
        
        paciente = PatientService.get_patient_by_id(db, patient_id)
        # Update only provided fields
        if 'direccion' in update_data and update_data['direccion']:
            paciente.direccion = update_data['direccion']

        if 'telefono' in update_data and update_data['telefono']:
            paciente.telefono_emergencia = update_data['telefono']
        
        if 'contacto_emergencia' in update_data and update_data['contacto_emergencia']:
            paciente.contacto_emergencia = update_data['contacto_emergencia']
        
        db.commit()
        db.refresh(paciente)
        
        return paciente
