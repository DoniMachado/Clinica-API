import asyncio
from database.connection import connection
from database.user import UserDatabase
from database.patient import PatientDatabase
from models.patient import Patient
from models.appointment import Appointment
from models.user import User
from models.integration import Integration
import security.hash as hs
import uuid
import consts.roles as r
from typing import List
from consts.appointment import WORKING_HOURS, APPOINTMENT_DURATION_MINUTES
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

async def clear_database():
    await Appointment.delete_all()
    await Patient.delete_all()
    await Integration.delete_all()
    await User.delete_all()

async def seed():
    await connection.initialize_database()

    userDatabase = UserDatabase()
    patientDatabase = PatientDatabase()

    print("Iniciando Restore do Banco Clinica-API!")

    print("Iniciando limpeza do banco...")
    await clear_database()
    print("Banco limpo!")

    print("Iniciando Restore de Users...")
    users: List[User] = [
        User(
            name = 'Adm 1',
            login = "adm.teste.1",
            email = 'adm.teste.1@email.com.br',
            password_hash = hs.hash_password('456'),
            audit_token = str(uuid.uuid4()),
            role = r.ADMIN_ROLE
        ),
        User(
            name = 'Adm 2',
            login = "adm.teste.2",
            email = 'adm.teste.2@email.com.br',
            password_hash = hs.hash_password('123'),
            audit_token = str(uuid.uuid4()),
            role = r.ADMIN_ROLE
        ),
        User(
            name = 'Doctor 1',
            login = "doctor.1",
            email = 'doctor.1@email.com.br',
            password_hash = hs.hash_password('senha'),
            audit_token = str(uuid.uuid4()),
            role = r.HEALTHCARE_PROFESSIONAL_ROLE
        ),
        User(
            name = 'Doctor 2',
            login = "doctor.2",
            email = 'doctor.2@email.com.br',
            password_hash = hs.hash_password('123'),
            audit_token = str(uuid.uuid4()),
            role = r.HEALTHCARE_PROFESSIONAL_ROLE
        ),
        User(
            name = 'Receptionist 1',
            login = "receptionist.1",
            email = 'receptionist.1@email.com.br',
            password_hash = hs.hash_password('123'),
            audit_token = str(uuid.uuid4()),
            role = r.RECEPTIONIST_ROLE
        ),
        User(
            name = 'Receptionist 2',
            login = "receptionist.2",
            email = 'receptionist.2@email.com.br',
            password_hash = hs.hash_password('123'),
            audit_token = str(uuid.uuid4()),
            role = r.RECEPTIONIST_ROLE
        )
    ]

    for user in users:
        await user.save()

    print("Finalizando o Restore de Users...")

    print("Iniciando Restore de Integrations...")

    integrations: List[Integration] = [
        Integration(
            client_name = "Parceiro Teste 1",
            client_id = "partner-test-1",
            client_secret_hash = hs.hash_password('123456'),
            audit_token = str(uuid.uuid4())
        )
    ]
    for integration in integrations:
        await integration.save()

    print("Finalizando o Restore de Integrations...")

    print("Iniciando Restore de Pacientes...")

    patients: List[Patient] = [
        Patient(
            name = 'Paciente 1',
            cpf = '555.555.555.14',
            email = 'paciente.1@email.com',
            phone = '(19) 99897-5555',
            address = None,
            birth_date = None,
            audit_token = str(uuid.uuid4())
        ),
        Patient(
            name = 'Paciente 2',
            cpf = '555.555.555.15',
            email = 'paciente.2@email.com',
            phone = '(19) 99897-5555',
            address = None,
            birth_date = None,
            audit_token = str(uuid.uuid4())
        )
    ]
    for patient in patients:
        await patient.save()

    print("Finalizando o Restore de Pacientes...")

    users = await userDatabase.get_all_by_role(r.HEALTHCARE_PROFESSIONAL_ROLE)
    patients = await patientDatabase.get_all()
    
    if users and patients and users[0] is not None:
        first_doctor = users[0]

        shift_start_time, shift_end_time = WORKING_HOURS[0]
        BRAZIL_TZ = ZoneInfo("America/Sao_Paulo")
        today = datetime.now(BRAZIL_TZ).date()
        shift_start = datetime.combine(today, shift_start_time, tzinfo=BRAZIL_TZ)
        shift_end = datetime.combine(today, shift_end_time, tzinfo=BRAZIL_TZ)

        print("Iniciando Restore de Agendamentos...")

        appointments: List[Appointment] = []


        appointment_start = shift_start
        appointment_end = shift_start + timedelta(minutes=APPOINTMENT_DURATION_MINUTES)

        for patient in patients:
            appointments.append(Appointment(
                patient_id = patient.id,
                doctor_id = first_doctor.id,
                start_at = appointment_start,
                end_at = appointment_end,
                audit_token = str(uuid.uuid4())
            ))

            appointment_start  = appointment_end
            appointment_end = appointment_end + timedelta(minutes=APPOINTMENT_DURATION_MINUTES)

        for appointment in appointments:
            await appointment.save()

        print("Finalizando o Restore de Agendamentos...")

    print("Finalizando o Restore do Banco Clinica-API!")

if __name__ == "__main__":
    asyncio.run(seed())