SYSTEM_ADMIN = "system:admin"

# Patient
PATIENT_READ = "patient:read"
PATIENT_CREATE = "patient:create"
PATIENT_UPDATE = "patient:update"
PATIENT_DELETE = "patient:delete"


# User / Employee
USER_READ = "user:read"
USER_CREATE = "user:create"
USER_UPDATE = "user:update"
USER_DELETE = "user:delete"


# Appointment
APPOINTMENT_READ = "appointment:read"
APPOINTMENT_CREATE = "appointment:create"
APPOINTMENT_UPDATE = "appointment:update"
APPOINTMENT_DELETE = "appointment:delete"

# Doctor Availability
AVAILABILITY_READ = "availability:read"

ALL_PERMISSIONS = [
    SYSTEM_ADMIN,
    PATIENT_READ,
    PATIENT_CREATE,
    PATIENT_UPDATE,
    PATIENT_DELETE,
    USER_READ,
    USER_CREATE,
    USER_UPDATE,
    USER_DELETE,
    APPOINTMENT_READ,
    APPOINTMENT_CREATE,
    APPOINTMENT_UPDATE,
    APPOINTMENT_DELETE,
    AVAILABILITY_READ
]