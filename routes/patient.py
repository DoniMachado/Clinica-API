from fastapi import APIRouter, HTTPException, status, Depends
from models.patient import *
from models.token_data import TokenData
import database.patient as p
import security.auth as auth
from typing import Dict, List
import consts.permissions as perm
from beanie import PydanticObjectId
import re

patient_router = APIRouter(
    tags=["Patient"]
)

patientDatabase = p.PatientDatabase()

@patient_router.get("/", response_model=List[PatientResponseDTO])
async def get_all_patients(token: TokenData = Depends(auth.validate_token)) -> List[PatientResponseDTO]:
    if not token.has_permission(perm.PATIENT_READ): 
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Can't access patient's data.") 

    return await patientDatabase.get_all()

@patient_router.get("/by-name/{name}", response_model=List[PatientResponseDTO])
async def get_patients_by_name(name: str, token: TokenData = Depends(auth.validate_token)) -> List[PatientResponseDTO]:
    if not token.has_permission(perm.PATIENT_READ): 
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Can't access patient's data.") 

    pattern = r"[a-zA-Z\s-]+"
    if not re.fullmatch(pattern, name):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid patient name.") 
    
    return await patientDatabase.get_by_name(name)

@patient_router.get("/by-name-vulnerable/{name}", response_model=List[PatientResponseDTO])
async def get_patients_by_name_vulnerable(name: str, token: TokenData = Depends(auth.validate_token)) -> List[PatientResponseDTO]:
    if not token.has_permission(perm.PATIENT_READ): 
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Can't access patient's data.") 

    pattern = r"[a-zA-Z\s-]+"
    if not re.fullmatch(pattern, name):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid patient name.") 
    
    return await patientDatabase.get_by_name_vulnerable(name)


@patient_router.get("/{id}", response_model=PatientResponseDTO)
async def get_patient(id: PydanticObjectId, token: TokenData = Depends(auth.validate_token)) -> PatientResponseDTO:
    if not token.has_permission(perm.PATIENT_READ): 
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Can't access patient's data.") 

    patient = await patientDatabase.get(id = id)

    if patient is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found.") 

    return patient

@patient_router.post("/new", status_code  = status.HTTP_201_CREATED,  response_model=PatientResponseDTO)
async def create_patient(body: PatientRequestDTO, token: TokenData = Depends(auth.validate_token)) -> PatientResponseDTO:
    if not token.has_permission(perm.PATIENT_CREATE): 
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Can't create patient's data.") 

    patient = await patientDatabase.create_patient(dto = body)
    if patient is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Couldn't create patient's data.") 
    
    return  patient

@patient_router.post("/new-unsafe-return", status_code  = status.HTTP_201_CREATED,  response_model=Patient)
async def create_patient_unsafe(body: PatientRequestDTO, token: TokenData = Depends(auth.validate_token)) -> Patient:
    if not token.has_permission(perm.PATIENT_CREATE): 
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Can't create patient's data.") 
    
    patient = await patientDatabase.create_patient(dto = body)
    if patient is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Couldn't create patient's data.") 
    
    return  patient

@patient_router.post("/new-form", status_code = status.HTTP_201_CREATED,  response_model=PatientResponseDTO)
async def create_patient_form(body: PatientRequestDTO = Depends(PatientRequestDTO.as_form), token: TokenData = Depends(auth.validate_token)) -> PatientResponseDTO:
    if not token.has_permission(perm.PATIENT_CREATE): 
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Can't create patient's data.") 
    
    patient = await patientDatabase.create_patient(dto = body)
    if patient is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Couldn't create patient's data.") 
    
    return  patient  


@patient_router.put("/edit/{id}", response_model=PatientResponseDTO)
async def edit_patient(id:PydanticObjectId , body: PatientRequestDTO, token: TokenData = Depends(auth.validate_token)) -> PatientResponseDTO:
    if not token.has_permission(perm.PATIENT_UPDATE): 
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Can't update patient's data.") 

    patient = await patientDatabase.get(id)
    if patient is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found.") 

    patient = await patientDatabase.edit_patient(id = id, dto = body)
    if patient is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Couldn't update patient's data.") 

    return patient


@patient_router.delete("/{id}")
async def delete_patient(id: PydanticObjectId, token: TokenData = Depends(auth.validate_token)) -> Dict:
    if not token.has_permission(perm.PATIENT_DELETE): 
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Can't delete patient's data.") 

    delete_success = await patientDatabase.delete(id = id)
    if not delete_success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Error on patient's data delete")
    
    return {
        "message": "Patient deleted successfully."
    }