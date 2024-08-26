# services/appointment_service.py

from database.db_connection import get_connection
from datetime import datetime, timedelta
import time

# services/appointment_service.py

from database.db_connection import get_connection
from datetime import datetime, timedelta
import math

def get_doctor_availability(doctor_id, date):
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        # Get doctor's schedule for the given day
        day_of_week = date.weekday() + 1  # Assuming 1-7 corresponds to Monday-Sunday
        query = """
        SELECT heureDeAm, heureAAm, heureDePm, heureAPm, m.duree_rdv
        FROM planning p
        JOIN medecin m ON p.id_medecin = m.id
        WHERE p.id_medecin = %s AND p.id_jour = %s
        """
        cursor.execute(query, (doctor_id, day_of_week))
        schedule = cursor.fetchone()

        if not schedule:
            return []

        # Get existing appointments for the doctor on the given date
        query = """
        SELECT DateDeb
        FROM rendezvous
        WHERE statut<>'A' AND MedecinId = %s AND DATE(DateDeb) = %s
        """
        cursor.execute(query, (doctor_id, date.date()))
        booked_slots = [row['DateDeb'] for row in cursor.fetchall()]

        # Calculate available time slots
        available_slots = []
        slot_duration = timedelta(minutes=schedule['duree_rdv'])

        current_time = datetime.now()
        buffer_time = timedelta(minutes=15)  # Add a 15-minute buffer
        
        for period in [('heureDeAm', 'heureAAm'), ('heureDePm', 'heureAPm')]:
            start_time = datetime.strptime(str(schedule[period[0]]), "%H:%M:%S").time()
            end_time = datetime.strptime(str(schedule[period[1]]), "%H:%M:%S").time()

            start = datetime.combine(date.date(), start_time)
            end = datetime.combine(date.date(), end_time)

            # If it's the current day, start from the current time plus buffer
            if date.date() == current_time.date():
                start = max(start, current_time + buffer_time)

                # Round up to the next available slot
                minutes_to_add = math.ceil((start - datetime.combine(start.date(), start.time().replace(hour=0, minute=0, second=0, microsecond=0))).total_seconds() / 60 / schedule['duree_rdv']) * schedule['duree_rdv']
                start = datetime.combine(start.date(), datetime.min.time()) + timedelta(minutes=minutes_to_add)

            current = start
            while current + slot_duration <= end:
                if current not in booked_slots:
                    available_slots.append(current.strftime("%H:%M"))
                current += slot_duration

        return available_slots

    except Exception as e:
        print(f"Error fetching doctor availability: {e}")
        return []
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def create_appointment(doctor_id, patient_id, appointment_datetime, reason, doctor_note=None):
    try:
        connection = get_connection()
        cursor = connection.cursor()

        # Check if the slot is still available
        check_query = """
        SELECT COUNT(*) FROM rendezvous
        WHERE MedecinId = %s AND DateDeb = %s AND statut <> 'A'
        """
        cursor.execute(check_query, (doctor_id, appointment_datetime))
        if cursor.fetchone()[0] > 0:
            return False, "This time slot is no longer available."

        # Insert the new appointment
        insert_query = """
        INSERT INTO rendezvous (MedecinId, PatientId, DateDeb, raison, statut, doctorNote)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query, (doctor_id, patient_id, appointment_datetime, reason, 'D', doctor_note or ''))  # 'D' for Demanded
        connection.commit()

        return True, "Appointment created successfully."

    except Exception as e:
        print(f"Error creating appointment: {e}")
        return False, str(e)
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def create_appointment(doctor_id, patient_id, appointment_datetime, reason, doctor_note=None):
    try:
        connection = get_connection()
        cursor = connection.cursor()

        # Check if the slot is still available
        check_query = """
        SELECT COUNT(*) FROM rendezvous
        WHERE MedecinId = %s AND DateDeb = %s AND statut <> 'A'
        """
        cursor.execute(check_query, (doctor_id, appointment_datetime))
        if cursor.fetchone()[0] > 0:
            return False, "This time slot is no longer available."

        # Insert the new appointment
        insert_query = """
        INSERT INTO rendezvous (MedecinId, PatientId, DateDeb, raison, statut, doctorNote)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query, (doctor_id, patient_id, appointment_datetime, reason, 'D', doctor_note or ''))  # 'D' for Demanded
        connection.commit()

        return True, "Appointment created successfully."

    except Exception as e:
        print(f"Error creating appointment: {e}")
        return False, str(e)
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            
def get_appointments_by_patient_id(patient_id):
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        query = """
        SELECT id, MedecinId, PatientId, DateDeb, raison, statut, doctorNote
        FROM rendezvous
        WHERE PatientId = %s
        """
        cursor.execute(query, (patient_id,))
        appointments = cursor.fetchall()

        return appointments

    except Exception as e:
        print(f"Error fetching appointments for patient {patient_id}: {e}")
        return []
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
     

# Update the update_appointment function
def update_appointment(appointment_id, patient_id, **kwargs):
    try:
        connection = get_connection()
        cursor = connection.cursor()
        
        # Check if the appointment exists and belongs to the given patient
        check_query = """
        SELECT * FROM rendezvous
        WHERE id = %s AND PatientId = %s
        """
        cursor.execute(check_query, (appointment_id, patient_id))
        appointment = cursor.fetchone()
        if not appointment:
            return False, "Appointment not found or does not belong to the patient."
        
        # Prepare the update query dynamically based on which fields are provided
        update_fields = []
        update_values = []
        
        if 'reason' in kwargs:
            update_fields.append("raison = %s")
            update_values.append(kwargs['reason'])
        if 'doctor_id' in kwargs:
            update_fields.append("MedecinId = %s")
            update_values.append(kwargs['doctor_id'])
        if 'appointment_datetime' in kwargs:
            update_fields.append("DateDeb = %s")
            update_values.append(kwargs['appointment_datetime'])
        if 'status' in kwargs:
            update_fields.append("statut = %s")
            update_values.append(kwargs['status'])
        
        if not update_fields:
            return False, "No updates provided."
        
        # Construct and execute the update query
        update_query = f"""
        UPDATE rendezvous
        SET {', '.join(update_fields)}
        WHERE id = %s AND PatientId = %s
        """
        update_values.extend([appointment_id, patient_id])
        cursor.execute(update_query, tuple(update_values))
        connection.commit()
        
        if cursor.rowcount == 0:
            return False, "No changes were made to the appointment."
        return True, "Appointment updated successfully."
    except Exception as e:
        print(f"Error updating appointment: {e}")
        return False, str(e)
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


def edit_appointment(appointment_id, patient_id, reason=None, status=None):
    try:
        connection = get_connection()
        cursor = connection.cursor()
        
        # Check if the appointment exists and belongs to the patient
        check_query = """
        SELECT * FROM rendezvous
        WHERE id = %s AND PatientId = %s AND statut = 'D'
        """
        cursor.execute(check_query, (appointment_id, patient_id))
        appointment = cursor.fetchone()
        if not appointment:
            return False, "Appointment not found, does not belong to the patient, or is not in 'Demanded' status."
        
        # Prepare the update query
        update_fields = []
        update_values = []
        
        if reason is not None:
            update_fields.append("raison = %s")
            update_values.append(reason)
        if status is not None:
            update_fields.append("statut = %s")
            update_values.append(status)
        
        if not update_fields:
            return False, "No updates provided."
        
        # Construct and execute the update query
        update_query = f"""
        UPDATE rendezvous
        SET {', '.join(update_fields)}
        WHERE id = %s AND PatientId = %s AND statut = 'D'
        """
        update_values.extend([appointment_id, patient_id])
        cursor.execute(update_query, tuple(update_values))
        connection.commit()
        
        if cursor.rowcount == 0:
            return False, "No changes were made to the appointment."
        return True, "Appointment updated successfully."
    except Exception as e:
        print(f"Error editing appointment: {e}")
        return False, str(e)
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()