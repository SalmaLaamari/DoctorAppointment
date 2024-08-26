from database.db_connection import get_connection
from models.ville import Ville

def find_all():
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM ville"
        cursor.execute(query)
        result = cursor.fetchall()
        return [Ville(**row) for row in result]
    except Exception as e:
        print(f"Error fetching all villes: {e}")
        return []
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()