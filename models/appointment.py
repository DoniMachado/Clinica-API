from pydantic import BaseModel, Field, ConfigDict, field_serializer, field_validator
from fastapi import Form
from beanie import Document, PydanticObjectId
from datetime import datetime
from enum import Enum
from configs.convert_datetime import *

class AppointmentStatus(str, Enum):
    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Appointment(Document):
    model_config = ConfigDict(from_attributes=True, extra="forbid")

    # _id é gerado e gerenciado pelo MongoDB/Beanie

    patient_id: PydanticObjectId = Field(
        description="Identificador do paciente"
    )

    doctor_id: PydanticObjectId = Field(
        description="Identificador do profissional de saúde"
    )

    start_at: datetime = Field(
        description="Data e hora de início da consulta"
    )

    end_at: datetime = Field(
        description="Data e hora de término da consulta"
    )

    status: AppointmentStatus = Field(
        default=AppointmentStatus.SCHEDULED,
        description="Status da consulta"
    )

    audit_token: str  = Field(
            description = "Token de auditoria",
            examples = ["550e8400-e29b-41d4-a716-446655440000"]
    )

    @field_validator("start_at", "end_at", mode="before")
    @classmethod
    def convert_to_utc(cls, value: datetime) -> datetime:
        return to_utc(value)        

    class Settings:
        name = "appointments"


class AppointmentResponseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra='ignore')

    id: PydanticObjectId = Field(
        description = "Identificador único do usuário",
        examples = ["68c123456789abcdef123456"]
    )

    patient_id: PydanticObjectId = Field(
        description="Identificador do paciente"
    )

    doctor_id: PydanticObjectId = Field(
        description="Identificador do profissional de saúde"
    )

    start_at: datetime = Field(
        description="Data e hora de início da consulta"
    )

    end_at: datetime = Field(
        description="Data e hora de término da consulta"
    )

    status: AppointmentStatus = Field(
        default=AppointmentStatus.SCHEDULED,
        description="Status da consulta"
    )

    
    @property
    def start_at_local(self) -> datetime:
        return from_utc(self.start_at)

    @property
    def end_at_local(self) -> datetime:
        return from_utc(self.end_at)

    @field_serializer("id", "patient_id", "doctor_id")
    def serialize_id(self, value: PydanticObjectId) -> str:
        return str(value)

    @field_serializer("start_at", "end_at")
    def serialize_datetime(self, value: datetime) -> str:
        return from_utc(value).isoformat()

class AppointmentRequestDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra='forbid')

    patient_id: PydanticObjectId = Field(
        description="Identificador do paciente"
    )

    doctor_id: PydanticObjectId = Field(
        description="Identificador do profissional de saúde"
    )

    start_at: datetime = Field(
        description="Data e hora de início da consulta"
    )

    end_at: datetime = Field(
        description="Data e hora de término da consulta"
    )

    @classmethod
    def as_form( cls, patient_id: PydanticObjectId = Form(...), doctor_id: PydanticObjectId = Form(...), start_at: datetime = Form(...),  end_at: datetime = Form(...) ):
        return cls(patient_id = patient_id, doctor_id = doctor_id,  start_at = start_at, end_at = end_at)