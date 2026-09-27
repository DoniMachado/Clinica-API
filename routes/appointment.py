from fastapi import APIRouter, HTTPException, status, Depends, Request
from models.appointment import *
from models.user import *
from models.patient import *
from models.token_data import TokenData
import database.appointment as a
import database.user as u
import database.patient as p
import security.auth as auth
from typing import Dict, List
import consts.permissions as perm
import consts.roles as roles
from consts.appointment import WORKING_HOURS, APPOINTMENT_DURATION_MINUTES, get_available_slots
from beanie import PydanticObjectId
from configs.templates import templates
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

appointment_router = APIRouter(
    tags=["Appointment"]
)

appointmentDatabase = a.AppointmentDatabase()
userDatabase = u.UserDatabase()
patientDatabase = p.PatientDatabase()
BRAZIL_TZ = ZoneInfo("America/Sao_Paulo")

@appointment_router.get("/", response_model=List[AppointmentResponseDTO])
async def get_all_appointments(token: TokenData = Depends(auth.validate_token)) -> List[AppointmentResponseDTO]:
    if not token.has_permission(perm.APPOINTMENT_READ): 
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Can't access appointment's data.") 

    if not token.has_role(roles.RECEPTIONIST_ROLE):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Can't access appointment's data.") 
    
    return await appointmentDatabase.get_all()

@appointment_router.get("/patient/{patient_id}", response_model=AppointmentResponseDTO)
async def get_patient_appointments(patient_id: PydanticObjectId, token: TokenData = Depends(auth.validate_token)) -> AppointmentResponseDTO:
    if not token.has_permission(perm.APPOINTMENT_READ): 
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Can't access appointment's data.") 

    if not token.has_role(roles.RECEPTIONIST_ROLE):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Can't access appointment's data.") 

    return await appointmentDatabase.get_all_by_patient_id(patient_id = patient_id)

@appointment_router.get("/doctor/{doctor_id}", response_model=AppointmentResponseDTO)
async def get_doctor_appointments(doctor_id: PydanticObjectId, token: TokenData = Depends(auth.validate_token)) -> AppointmentResponseDTO:
    if not token.has_permission(perm.APPOINTMENT_READ): 
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Can't access appointment's data.") 

    if not token.has_role(roles.RECEPTIONIST_ROLE):
        if not token.has_owner_id(doctor_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Can't access another doctor appointment's data.") 

    return await appointmentDatabase.get_all_by_doctor_id(doctor_id = doctor_id)

@appointment_router.get("/doctor/availabity/{doctor_id}")
async def get_doctor_availabity(doctor_id: PydanticObjectId, token: TokenData = Depends(auth.validate_token)):
    if not token.has_permission(perm.AVAILABILITY_READ): 
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Can't access appointment's data.") 

    if not token.has_role(roles.RECEPTIONIST_ROLE) and not token.has_role(roles.INTEGRATION_ROLE):
        if not token.has_owner_id(doctor_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Can't access another doctor appointment's data.") 

    doctor = await userDatabase.get(doctor_id)
    if doctor is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor not found")

    if doctor.role != roles.HEALTHCARE_PROFESSIONAL_ROLE:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="This user is not a doctor")
    
    appointments = await appointmentDatabase.get_all_by_doctor_id(doctor_id = doctor_id)
    available_slots = get_available_slots(appointments)
    return available_slots

@appointment_router.get("/{id}", response_model=AppointmentResponseDTO)
async def get_appointment(id: PydanticObjectId, token: TokenData = Depends(auth.validate_token)) -> AppointmentResponseDTO:
    if not token.has_permission(perm.APPOINTMENT_READ): 
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Can't access appointment's data.") 

    appointment = await appointmentDatabase.get(id = id)

    if appointment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found.") 

    if not token.has_role(roles.RECEPTIONIST_ROLE):
        if not token.has_owner_id(appointment.doctor_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Can't access another doctor appointment's data.") 

    return appointment

@appointment_router.get("/{id}/html") # Use o cookie o"access_token" com o valor do token para conseguir acessar essa rota
async def get_appointment_html(request: Request, id: PydanticObjectId, token: TokenData = Depends(auth.validate_token)):
    if not token.has_permission(perm.APPOINTMENT_READ): 
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Can't access appointment's data.") 

    appointment = await appointmentDatabase.get(id = id)

    if appointment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found.") 

    if not token.has_role(roles.RECEPTIONIST_ROLE):
        if not token.has_owner_id(appointment.doctor_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Can't access another doctor appointment's data.") 

    appointment_dto = AppointmentResponseDTO.model_validate(appointment)

    doctor = await userDatabase.get(appointment.doctor_id)
    doctor_dto = UserResponseDTO.model_validate(doctor)

    patient = await patientDatabase.get(appointment.patient_id)
    patient_dto = PatientResponseDTO.model_validate(patient)

    return templates.TemplateResponse(
        request = request,
        name = "appointment/appointment.html",
        context = {
            "appointment" : appointment_dto,
            "doctor": doctor_dto,
            "patient": patient_dto 
        }
    )

@appointment_router.post("/new", status_code  = status.HTTP_201_CREATED,  response_model=AppointmentResponseDTO)
async def create_appointment(body: AppointmentRequestDTO, token: TokenData = Depends(auth.validate_token)) -> AppointmentResponseDTO:
    if not token.has_permission(perm.PATIENT_CREATE): 
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Can't create appointment's data.") 

    if not token.has_role(roles.RECEPTIONIST_ROLE):
        if not token.has_owner_id(body.doctor_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Can't create another doctor appointment's data.") 

    if body.start_at >= body.end_at:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid start_at and end_at")

    diff_minutes = (body.end_at - body.start_at).total_seconds() //60
    if diff_minutes > APPOINTMENT_DURATION_MINUTES: 
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid start_at and end_at")

    is_valid = any(start <= body.start_at.time() <= end for start, end in WORKING_HOURS)
    if not is_valid: 
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid start_at time")

    is_valid = any(start <= body.end_at.time() <= end for start, end in WORKING_HOURS)
    if not is_valid: 
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid end_at time")

    doctor = await userDatabase.get(body.doctor_id)
    if doctor is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor not found")

    if doctor.role != roles.HEALTHCARE_PROFESSIONAL_ROLE:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="This user is not a doctor")

    patient = await patientDatabase.get(body.patient_id)
    if patient is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")

    appointment = await appointmentDatabase.create_appointment(dto = body)
    if appointment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Couldn't create appointment's data.") 
    
    return  appointment

@appointment_router.put("/edit/{id}", response_model=AppointmentResponseDTO)
async def edit_appointment(id:PydanticObjectId , body: AppointmentRequestDTO, token: TokenData = Depends(auth.validate_token)) -> AppointmentResponseDTO:
    if not token.has_permission(perm.PATIENT_UPDATE): 
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Can't update appointment's data.") 

    appointment = await appointmentDatabase.get(id)
    if appointment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found.") 

    if not token.has_role(roles.RECEPTIONIST_ROLE):
        if not token.has_owner_id(appointment.doctor_id) or not token.has_owner_id(body.doctor_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Can't update another doctor appointment's data.") 

    if body.start_at >= body.end_at:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid start_at and end_at")

    diff_minutes = (body.end_at - body.start_at).total_seconds() //60
    if diff_minutes > APPOINTMENT_DURATION_MINUTES: 
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid start_at and end_at")

    is_valid = any(start <= body.start_at.time() <= end for start, end in WORKING_HOURS)
    if not is_valid: 
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid start_at time")

    is_valid = any(start <= body.end_at.time() <= end for start, end in WORKING_HOURS)
    if not is_valid: 
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid end_at time")

    doctor = await userDatabase.get(body.doctor_id)
    if doctor is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor not found")

    if doctor.role != roles.HEALTHCARE_PROFESSIONAL_ROLE:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="This user is not a doctor")

    appointment = await appointmentDatabase.edit_appointment(id = id, dto = body)
    if appointment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Couldn't update appointment's data.") 

    return appointment

@appointment_router.delete("/{id}")
async def delete_appointment(id: PydanticObjectId, token: TokenData = Depends(auth.validate_token)) -> Dict:
    if not token.has_permission(perm.APPOINTMENT_DELETE): 
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Can't delete appointment's data.") 

    appointment = await appointmentDatabase.get(id)
    if appointment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found.") 
    
    if not token.has_role(roles.RECEPTIONIST_ROLE):
        if not token.has_owner_id(appointment.doctor_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Can't delete another doctor appointment's data.") 

    delete_success = await appointmentDatabase.delete(id = id)
    if not delete_success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Error on appointment's data delete")
    
    return {
        "message": "Appointment deleted successfully."
    }