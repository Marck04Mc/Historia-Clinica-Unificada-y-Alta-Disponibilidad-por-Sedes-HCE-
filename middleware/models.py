"""
Modelos Pydantic para validación de datos
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime, date
from enum import Enum


# =====================================================
# Enums
# =====================================================

class RolEnum(str, Enum):
    paciente = "paciente"
    admisionista = "admisionista"
    medico = "medico"
    historificacion = "historificacion"
    admin = "admin"


class GeneroEnum(str, Enum):
    M = "M"
    F = "F"
    O = "O"


class TipoIdentificacionEnum(str, Enum):
    CC = "CC"
    TI = "TI"
    CE = "CE"
    PA = "PA"
    RC = "RC"


class TipoEncuentroEnum(str, Enum):
    consulta = "consulta"
    urgencia = "urgencia"
    hospitalizacion = "hospitalizacion"
    control = "control"
    cirugia = "cirugia"


# =====================================================
# Modelos de Usuario y Autenticación
# =====================================================

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None
    rol: Optional[str] = None
    id_sede: Optional[int] = None
    id_usuario: Optional[int] = None


class User(BaseModel):
    id_usuario: int
    username: str
    rol: RolEnum
    id_sede: Optional[int] = None
    nombres: Optional[str] = None
    apellidos: Optional[str] = None
    email: Optional[EmailStr] = None
    activo: bool = True


class UserInDB(User):
    password_hash: str


# =====================================================
# Modelos de Paciente
# =====================================================

class PacienteBase(BaseModel):
    identificacion: str
    tipo_identificacion: TipoIdentificacionEnum
    nombres: str
    apellidos: str
    fecha_nacimiento: date
    genero: GeneroEnum
    telefono: Optional[str] = None
    email: Optional[EmailStr] = None
    direccion: Optional[str] = None
    ciudad: Optional[str] = None


class PacienteCreate(PacienteBase):
    pass


class Paciente(PacienteBase):
    id_paciente: int
    id_usuario: Optional[int] = None
    fecha_registro: datetime
    activo: bool

    class Config:
        from_attributes = True


# =====================================================
# Modelos de Encuentro Clínico
# =====================================================

class EncuentroClinicoBase(BaseModel):
    id_paciente: int
    tipo_encuentro: TipoEncuentroEnum
    motivo_consulta: Optional[str] = None
    notas_clinicas: Optional[str] = None


class EncuentroClinicoCreate(EncuentroClinicoBase):
    pass


class EncuentroClinico(EncuentroClinicoBase):
    id_encuentro: int
    id_sede: int
    id_doctor: int
    fecha_hora: datetime
    estado: str

    class Config:
        from_attributes = True


# =====================================================
# Modelos de Observación Clínica
# =====================================================

class ObservacionClinicaBase(BaseModel):
    id_encuentro: int
    id_paciente: int
    codigo_loinc: Optional[str] = None
    descripcion: str
    valor_numerico: Optional[float] = None
    valor_texto: Optional[str] = None
    unidad: Optional[str] = None
    rango_referencia: Optional[str] = None
    interpretacion: Optional[str] = None


class ObservacionClinicaCreate(ObservacionClinicaBase):
    pass


class ObservacionClinica(ObservacionClinicaBase):
    id_observacion: int
    fecha_hora: datetime

    class Config:
        from_attributes = True


# =====================================================
# Modelos de Diagnóstico
# =====================================================

class DiagnosticoBase(BaseModel):
    id_encuentro: int
    id_paciente: int
    codigo_icd10: Optional[str] = None
    codigo_snomed: Optional[str] = None
    descripcion: str
    tipo: Optional[str] = None
    estado: str = "activo"


class DiagnosticoCreate(DiagnosticoBase):
    pass


class Diagnostico(DiagnosticoBase):
    id_diagnostico: int
    fecha_diagnostico: datetime

    class Config:
        from_attributes = True


# =====================================================
# Modelos de Medicamento
# =====================================================

class MedicamentoBase(BaseModel):
    id_encuentro: int
    id_paciente: int
    nombre: str
    principio_activo: Optional[str] = None
    dosis: Optional[str] = None
    frecuencia: Optional[str] = None
    duracion: Optional[str] = None
    via_administracion: Optional[str] = None
    indicaciones: Optional[str] = None


class MedicamentoCreate(MedicamentoBase):
    pass


class Medicamento(MedicamentoBase):
    id_medicamento: int
    fecha_prescripcion: datetime
    estado: str

    class Config:
        from_attributes = True


# =====================================================
# Modelos de Sede
# =====================================================

class Sede(BaseModel):
    id_sede: int
    nombre: str
    ciudad: str
    direccion: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[EmailStr] = None
    activo: bool

    class Config:
        from_attributes = True


# =====================================================
# Modelos de Respuesta
# =====================================================

class HistoriaClinicaCompleta(BaseModel):
    paciente: Paciente
    encuentros: List[EncuentroClinico]
    observaciones: List[ObservacionClinica]
    diagnosticos: List[Diagnostico]
    medicamentos: List[Medicamento]
