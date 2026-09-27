from models.patient import Patient, PatientRequestDTO
import uuid
from database.connection import Database
from beanie import PydanticObjectId
import re
import json
from typing import List

class PatientDatabase(Database[Patient]):

    def __init__(self):
        super().__init__(Patient)

    async def get_by_cpf(self, cpf: str) -> Patient | None:
        return await self.model.find_one(
            Patient.cpf == cpf
        )   

    async def get_by_email(self, email: str) -> Patient | None:
        return await self.model.find_one(
            Patient.email == email
        ) 

    async def get_by_name(self, name: str) -> List[Patient]:
        name_escaped = re.escape(name)

        return await self.model.find(
            {"name": {"$regex": name_escaped, "$options": "i"}}
        ).to_list()

    async def get_by_name_vulnerable(self, name: str) -> List[Patient]:
        query_str = f'{{"name": {{"$regex": "{name}", "$options": "i"}}}}'

        try:
            query = json.loads(query_str) 
            return await self.model.find(query).to_list()
        except Exception as ex:
            raise ex 

    async def create_patient(self, dto: PatientRequestDTO) -> Patient | None:
        if dto is None:
            return None

        existing_patient = await self.get_by_cpf(cpf = dto.cpf)

        if existing_patient is not None:
            return None

        existing_patient = await self.get_by_email(email = dto.email)

        if existing_patient is not None:
            return None

        patient = Patient(
            name = dto.name,
            cpf = dto.cpf,            
            email = dto.email,
            phone = dto.phone,
            address = dto.address,
            birth_date = dto.birth_date,
            audit_token = str(uuid.uuid4())
        )

        return await patient.save()

    async def edit_patient(self, id: PydanticObjectId, dto: PatientRequestDTO) -> Patient | None:
        if dto is None:
            return None

        patient = await self.get(id = id)

        if patient is None:
            return None

        if patient.cpf != dto.cpf:
            existing_patient = await self.get_by_cpf(cpf = dto.cpf)

            if existing_patient is not None and existing_patient.id != id:
                return None

        if patient.email != dto.email:
            existing_patient = await self.get_by_email(email = dto.email)

            if existing_patient is not None and existing_patient.id != id:
                return None

        patient.name = dto.name       
        patient.phone = dto.phone
        patient.address = dto.address
        patient.birth_date = dto.birth_date      

        return await self.update(id = id, body = patient)