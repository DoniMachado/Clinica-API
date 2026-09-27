import consts.permissions as p
import consts.roles as r

ROLE_PERMISSIONS = {
    r.ADMIN_ROLE: [
        p.SYSTEM_ADMIN
    ],
    r.RECEPTIONIST_ROLE: [
        p.PATIENT_READ,
        p.PATIENT_CREATE,     
        p.PATIENT_UPDATE,
        #p.PATIENT_DELETE,
        p.APPOINTMENT_READ,
        p.APPOINTMENT_CREATE,
        p.APPOINTMENT_UPDATE,
        p.APPOINTMENT_DELETE,
        p.AVAILABILITY_READ
    ],
    r.HEALTHCARE_PROFESSIONAL_ROLE: [
        p.PATIENT_READ,
        p.PATIENT_CREATE,     
        p.PATIENT_UPDATE,
        #p.PATIENT_DELETE,
        p.APPOINTMENT_READ,
        p.APPOINTMENT_CREATE,
        p.APPOINTMENT_UPDATE,
        p.APPOINTMENT_DELETE,
        p.AVAILABILITY_READ
    ],
    r.INTEGRATION_ROLE: [
        p.AVAILABILITY_READ
    ]
}