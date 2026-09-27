from models.appointment import Appointment, AppointmentRequestDTO, AppointmentStatus
import uuid
from database.connection import Database
from beanie import PydanticObjectId
from typing import List
from datetime import datetime

class AppointmentDatabase(Database[Appointment]):

    def __init__(self):
        super().__init__(Appointment)

    async def get_all_by_patient_id(self, patient_id: PydanticObjectId) ->  List[Appointment]:
        return await self.model.find(Appointment.patient_id == patient_id).to_list()

    async def get_all_by_doctor_id(self, doctor_id: PydanticObjectId) -> List[Appointment]:
        return await self.model.find(Appointment.doctor_id == doctor_id).to_list()

    async def get_by_patient_id_and_start_at_and_end_at(self, patient_id: PydanticObjectId, start_at: datetime, end_at: datetime) ->  Appointment | None:
        return await self.model.find_one(Appointment.patient_id == patient_id and Appointment.start_at >= start_at and Appointment.end_at <= end_at)

    async def get_by_doctor_id_and_start_at_and_end_at(self, doctor_id: PydanticObjectId, start_at: datetime, end_at: datetime) ->  Appointment | None:
        return await self.model.find_one(Appointment.doctor_id == doctor_id and Appointment.start_at >= start_at and Appointment.end_at <= end_at)
    
    async def create_appointment(self, dto: AppointmentRequestDTO) -> Appointment | None:
        if dto is None:
            return None

        existing_appointment = await self.get_by_patient_id_and_start_at_and_end_at(patient_id = dto.patient_id, start_at = dto.start_at, end_at = dto.end_at)

        if existing_appointment is not None:
            return None

        existing_appointment = await self.get_by_doctor_id_and_start_at_and_end_at(doctor_id = dto.doctor_id, start_at = dto.start_at, end_at = dto.end_at)

        if existing_appointment is not None:
            return None
        
        appointment = Appointment(
            doctor_id = dto.doctor_id,
            patient_id = dto.patient_id,
            start_at = dto.start_at, 
            end_at = dto.end_at,
            status = AppointmentStatus.SCHEDULED, 
            audit_token = str(uuid.uuid4())
        )

        return await appointment.save()

    async def edit_appointment(self, id: PydanticObjectId, dto: AppointmentRequestDTO) -> Appointment | None:
        if dto is None:
            return None

        appointment = await self.get(id = id)

        if appointment is None:
            return None

        if appointment.start_at != dto.start_at or appointment.end_at != dto.end_at:
            existing_appointment = await self.get_by_patient_id_and_start_at_and_end_at(patient_id = dto.patient_id, start_at = dto.start_at, end_at = dto.end_at)

            if existing_appointment is not None and existing_appointment.id != id:
                return None

        if appointment.doctor_id != dto.doctor_id:
            existing_appointment = await self.get_by_doctor_id_and_start_at_and_end_at(doctor_id = dto.doctor_id, start_at = dto.start_at, end_at = dto.end_at)

            if existing_appointment is not None and existing_appointment.id != id:
                return None             

        return await self.update(id = id, body = appointment)

    async def cancel_appointment(self, id: PydanticObjectId) -> Appointment | None:         
        appointment = await self.get(id = id)

        if appointment is None:
            return None

        appointment.status = AppointmentStatus.CANCELLED

        return await self.update(id = id, body = appointment)

    async def complete_appointment(self, id: PydanticObjectId) -> Appointment | None:         
        appointment = await self.get(id = id)

        if appointment is None:
            return None

        appointment.status = AppointmentStatus.COMPLETED

        return await self.update(id = id, body = appointment)