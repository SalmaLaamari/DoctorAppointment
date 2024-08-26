from database.db_connection import get_connection
from models.patient import Patient
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

def register_patient(patient: Patient):
    try:
        connection = get_connection()
        cursor = connection.cursor()

        # Hash the password before storing it
        hashed_password = bcrypt.generate_password_hash(patient.password).decode('utf-8')

        query = """
        INSERT INTO patient (nom, prenom, email, password, cin, dateNaissance, sexe, telephone, statut, dateInscription)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = (patient.nom, patient.prenom, patient.email, hashed_password, patient.cin,
                  patient.date_naissance, patient.sexe, patient.telephone, patient.statut, patient.date_inscription)

        cursor.execute(query, values)
        connection.commit()

        # Get the last inserted id
        patient.id = cursor.lastrowid

        return True
    except Exception as e:
        print(f"Error registering patient: {e}")
        return False
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
                        

def login_patient(email: str, password: str):
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        query = "SELECT * FROM patient WHERE email = %s"
        cursor.execute(query, (email,))

        patient_data = cursor.fetchone()

        if patient_data and bcrypt.check_password_hash(patient_data['password'], password):
            return Patient(
                patient_data['id'],
                patient_data['nom'],
                patient_data['prenom'],
                patient_data['email'],
                patient_data['password'],
                patient_data['cin'],
                patient_data['dateNaissance'],
                patient_data['sexe'],
                patient_data['telephone'],
                patient_data['statut'],
                patient_data['dateInscription']
            )
        else:
            return None
    except Exception as e:
        print(f"Error logging in patient: {e}")
        return None
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


def edit_patient(patient_id, updated_data):
    try:
        connection = get_connection()
        cursor = connection.cursor()

        # Prepare the SQL query
        query = """
        UPDATE patient 
        SET nom = %s, prenom = %s, email = %s, cin = %s, dateNaissance = %s, sexe = %s, telephone = %s
        WHERE id = %s
        """
        
        # Extract values from updated_data
        values = (
            updated_data['nom'],
            updated_data['prenom'],
            updated_data['email'],
            updated_data['cin'],
            updated_data['date_naissance'],
            updated_data['sexe'],
            updated_data['telephone'],
            patient_id
        )

        cursor.execute(query, values)
        connection.commit()

        return True, "Patient data updated successfully"
    except Exception as e:
        print(f"Error updating patient data: {e}")
        return False, str(e)
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()            