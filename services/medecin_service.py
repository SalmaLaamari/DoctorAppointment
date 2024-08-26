from database.db_connection import get_connection
from models.medecin import Medecin

def find_doctor_by_nom_and_prenom_or_ville_or_speciality(nom_prenom=None, ville_id=None, speciality_id=None):
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        
        query = """
        SELECT DISTINCT m.* 
        FROM medecin m
        LEFT JOIN ville v ON m.id_ville = v.id
        LEFT JOIN specialite s ON m.id_specialite = s.id
        WHERE m.active = 1
        """
        params = []
        conditions = []

        if nom_prenom:
            conditions.append("(m.nom LIKE %s OR m.prenom LIKE %s)")
            params.extend([f"%{nom_prenom}%", f"%{nom_prenom}%"])
        if ville_id:
            conditions.append("v.id = %s")
            params.append(ville_id)
        if speciality_id:
            conditions.append("s.id = %s")
            params.append(speciality_id)

        if conditions:
            query += " AND " + " AND ".join(conditions)

        cursor.execute(query, tuple(params))
        result = cursor.fetchall()
        return [Medecin(**row) for row in result]
    except Exception as e:
        print(f"Error fetching doctors: {e}")
        return []
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def find_doctor_by_id(doctor_id):
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        
        query = """
        SELECT m.* 
        FROM medecin m
        WHERE m.id = %s AND m.active = 1
        """
        params = [doctor_id]

        cursor.execute(query, tuple(params))
        result = cursor.fetchone()
        
        if result:
            return Medecin(**result)
        else:
            return None
    except Exception as e:
        print(f"Error fetching doctor by ID: {e}")
        return None
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()