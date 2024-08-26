from database.db_connection import get_connection
from models.specialite import Specialite

def find_all():
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM specialite"
        cursor.execute(query)
        result = cursor.fetchall()
        return [Specialite(**row) for row in result]
    except Exception as e:
        print(f"Error fetching all specialites: {e}")
        return []
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()