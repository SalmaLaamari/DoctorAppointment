from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime


# Import service functions
from services.medecin_service import *
from services.patient_service import register_patient, login_patient, edit_patient
from services.specialite_service import find_all as find_all_specialites
from services.ville_service import find_all as find_all_villes
from models.patient import Patient
from services.appointment_service import *

app = Flask(__name__)
CORS(app)


@app.route('/find_doctors', methods=['GET'])
def find_doctors():
    try:
        nom_prenom = request.args.get('nom_prenom')
        ville_id = request.args.get('ville_id', type=int)
        speciality_id = request.args.get('speciality_id', type=int)
        
        doctors = find_doctor_by_nom_and_prenom_or_ville_or_speciality(
            nom_prenom=nom_prenom,
            ville_id=ville_id,
            speciality_id=speciality_id
        )
        
        return jsonify([doctor.__dict__ for doctor in doctors]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/register', methods=['POST'])
def register():
    data = request.json
    new_patient = Patient(
        id=None,  # Set to None as it will be assigned by the database
        nom=data['nom'],
        prenom=data['prenom'],
        email=data['email'],
        password=data['password'],
        cin=data['cin'],
        date_naissance=data['date_naissance'],
        sexe=data['sexe'],
        telephone=data['telephone']
    )
    if register_patient(new_patient):
        return jsonify({"message": "Patient registered successfully.", "patient_id": new_patient.id}), 201
    else:
        return jsonify({"message": "Failed to register patient."}), 400

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    logged_in_patient = login_patient(data['email'], data['password'])
    if logged_in_patient:
        return jsonify({
            "message": "Login successful",
            "patient": logged_in_patient.to_dict()
        }), 200
    else:
        app.logger.error(f"Login failed for email: {data['email']}")
        return jsonify({"message": "Login failed"}), 401


@app.route('/specialites', methods=['GET'])
def get_all_specialites():
    specialites = find_all_specialites()
    return jsonify([specialite.to_dict() for specialite in specialites]), 200

@app.route('/villes', methods=['GET'])
def get_all_villes():
    villes = find_all_villes()
    return jsonify([ville.to_dict() for ville in villes]), 200
    
@app.route('/doctor-availability/<int:doctor_id>', methods=['GET'])
def doctor_availability(doctor_id):
    date_str = request.args.get('date')
    if not date_str:
        return jsonify({"error": "Date parameter is required"}), 400

    try:
        date = datetime.strptime(date_str, "%Y-%m-%d")
        current_time = datetime.now()
        
        # If the requested date is today, use current time
        if date.date() == current_time.date():
            date = current_time

    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400

    available_slots = get_doctor_availability(doctor_id, date)
    return jsonify({"available_slots": available_slots}), 200

@app.route('/create-appointment', methods=['POST'])
def create_new_appointment():
    data = request.json
    print('Received appointment data:', data)
    required_fields = ['doctor_id', 'patient_id', 'appointment_date', 'appointment_time', 'reason']
    
    for field in required_fields:
        if field not in data:
            print(f'Missing field: {field}')
            return jsonify({"error": f"Missing required field: {field}"}), 400
        
    try:
        # Parse the date and time
        appointment_datetime = datetime.strptime(f"{data['appointment_date']} {data['appointment_time']}", "%Y-%m-%d %H:%M:%S")

        # Create the appointment
        success, message = create_appointment(
            data['doctor_id'],
            data['patient_id'],
            appointment_datetime,
            data['reason'],
            data.get('doctor_note')  # This will be None if not provided
        )

        if success:
            return jsonify({"message": message}), 201
        else:
            return jsonify({"error": message}), 400

    except ValueError as e:
        return jsonify({"error": f"Invalid date or time format: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


@app.route('/appointments/<int:patient_id>', methods=['GET'])
def get_appointments(patient_id):
    try:
        appointments = get_appointments_by_patient_id(patient_id)
        return jsonify({"appointments": appointments}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/edit-patient/<int:patient_id>', methods=['PUT'])
def edit_patient_route(patient_id):
    data = request.json
    success, message = edit_patient(patient_id, data)
    if success:
        return jsonify({"message": message}), 200
    else:
        return jsonify({"error": message}), 400
    
@app.route('/doctor/<int:doctor_id>', methods=['GET'])
def get_doctor_by_id(doctor_id):
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        query = """
        SELECT * FROM medecin WHERE id = %s AND active = 1
        """
        cursor.execute(query, (doctor_id,))
        result = cursor.fetchone()

        if result:
            doctor = Medecin(**result)
            return jsonify(doctor.to_dict()), 200
        else:
            return jsonify({"message": "Doctor not found"}), 404
    except Exception as e:
        print(f"Error fetching doctor by ID: {e}")
        return jsonify({"message": "Internal server error"}), 500
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

@app.route('/update-appointment/<int:appointment_id>', methods=['PUT'])
def update_appointment_route(appointment_id):
    data = request.json
    patient_id = data.get('patient_id')
    if not patient_id:
        return jsonify({"error": "patient_id is required"}), 400
    
    # Collect all possible update fields
    updates = {}
    if 'reason' in data:
        updates['reason'] = data['reason']
    if 'doctor_id' in data:
        updates['doctor_id'] = data['doctor_id']
    if 'status' in data:
        updates['status'] = data['status']
    if 'appointment_date' in data and 'appointment_time' in data:
        try:
            appointment_datetime = datetime.strptime(f"{data['appointment_date']} {data['appointment_time']}", "%Y-%m-%d %H:%M")
            updates['appointment_datetime'] = appointment_datetime
        except ValueError as e:
            return jsonify({"error": f"Invalid date or time format: {str(e)}"}), 400

    success, message = update_appointment(appointment_id, patient_id, **updates)
    if success:
        return jsonify({"message": message}), 200
    else:
        return jsonify({"error": message}), 400
    
@app.route('/edit-appointment/<int:appointment_id>', methods=['PUT'])
def edit_appointment_route(appointment_id):
    data = request.json
    patient_id = data.get('patient_id')
    if not patient_id:
        return jsonify({"error": "patient_id is required"}), 400
    
    reason = data.get('reason')
    status = data.get('status')

    success, message = edit_appointment(appointment_id, patient_id, reason=reason, status=status)
    if success:
        return jsonify({"message": message}), 200
    else:
        return jsonify({"error": message}), 400
        
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')