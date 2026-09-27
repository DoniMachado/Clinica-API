from datetime import time, datetime, timedelta
from configs.convert_datetime import APP_TIMEZONE

WORKING_HOURS = [
    (time(8, 0), time(12, 0)),
    (time(14, 0), time(18, 0)),
]

APPOINTMENT_DURATION_MINUTES = 30


def get_available_slots(appointments):
    available = []

    for work_start, work_end in WORKING_HOURS:
        current = datetime.combine(datetime.today(), work_start, tzinfo=APP_TIMEZONE)
        end = datetime.combine(datetime.today(), work_end, tzinfo=APP_TIMEZONE)

        while current + timedelta(minutes=APPOINTMENT_DURATION_MINUTES) <= end:

            slot_start = current
            slot_end = current + timedelta(minutes=APPOINTMENT_DURATION_MINUTES)

            has_conflict = any(
                appointment.start_at < slot_end
                and appointment.end_at > slot_start
                for appointment in appointments
            )

            if not has_conflict:
                available.append(
                    (
                        slot_start.time(),
                        slot_end.time()
                    )
                )

            current += timedelta(minutes=APPOINTMENT_DURATION_MINUTES)

    return available