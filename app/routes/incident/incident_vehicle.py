from flask_jwt_extended import get_jwt_identity
from app.extensions import db
from marshmallow import ValidationError
from flask import Blueprint, request, jsonify
from utils.datetime import get_current_time_in_timezone
from utils import auth
from app.models.models import Incident, IncidentStatus, Vehicle, IncidentVehicle, IncidentVehicleStatus, Driver

incident_vehicle_route = Blueprint('incidents/vehicles', __name__)

# Ambil Data
@incident_vehicle_route.route('/', methods=['GET'])
@auth.login_required
def get_incident_vehicle():
    # Ambil user berdasarkan data login
    user_id = get_jwt_identity()
    vehicle_id = Vehicle.query.filter_by(user_id = user_id).with_entities(Vehicle.id).scalar()
    
    # Ambil parameter query status (ditolak, dilaporkan, ditangani, selesai)
    status = request.args.get('status', None)
    
    # Bangun kueri
    incidents = db.session.query(
        Incident.id.label('incident_id'),
        Incident.description,
        Incident.reported_at,
        Incident.picture,
        Incident.status,
    ).filter(
        Incident.status == status
    ).filter_by(
        vehicle_id = vehicle_id
    ).all()  # Gunakan alias di sini

    # Siapkan datanya
    incident_data = [
        {
            "id": incident.incident_id,
            "description": incident.description,
            "reported_at": incident.reported_at.strftime('%H:%M'),  # Format jam dan menit
            "picture": incident.picture,
            "status": incident.status,
        }
        for incident in incidents
    ]

    return jsonify(
        status=True,
        message='Insiden berhasil dimuat.',
        data=incident_data
    ), 200
# Akhir Ambil Data

# Ambil Data ditolak berdasarkan ID
@incident_vehicle_route.route('/<int:incident_id>', methods=['GET'])
@auth.login_required
def get_incident_vehicle_by_id(incident_id):
    # Ambil parameter query status (ditolak, dilaporkan, ditangani, selesai)
    status = request.args.get('status', None)
    
    # Query untuk mendapatkan data incident berdasarkan ID
    incident = db.session.query(Incident).filter_by(id=incident_id).filter(
        Incident.status == status
    ).first()

    # Jika data tidak ditemukan
    if not incident:
        return jsonify(
            status=False,
            message='Insiden tidak ditemukan.',
        ), 404

    # Menyiapkan data untuk respons
    if incident.status == IncidentStatus.REPORTED:
        incident_data = {
            "id": incident.id,
            "status": incident.status,
            "description": incident.description,
            "reported_at": incident.reported_at,
            "location": {
                "latitude": incident.latitude,
                "longitude": incident.longitude
            },
            "picture": incident.picture,
            "status": incident.status,
            "resident": {
                "id": incident.resident.id,
                "user": {
                    "id": incident.resident.user.id,  # Akses User dari Resident
                    "name": incident.resident.user.name,  # Akses User's name
                    "avatar": incident.resident.user.avatar  # Akses User's address
                }
            },
            "institution": {
                "id": incident.institution.id,
                "user": {
                    "name": incident.institution.user.name,  # Akses User's name di Vehicle
                    "address": incident.institution.user.address,  # Akses User's address di Vehicle
                    "avatar": incident.institution.user.avatar,  # Akses User's avatar di Vehicle
                },
            }
        }
    elif incident.status == IncidentStatus.HANDLED:
        incident_data = {
            "id": incident.id,
            "status": incident.status,
            "description": incident.description,
            "reported_at": incident.reported_at,
            "location": {
                "latitude": incident.latitude,
                "longitude": incident.longitude
            },
            "picture": incident.picture,
            "status": incident.status,
            "resident": {
                "id": incident.resident.id,
                "user": {
                    "id": incident.resident.user.id,  # Akses User dari Resident
                    "name": incident.resident.user.name,  # Akses User's name
                    "avatar": incident.resident.user.avatar  # Akses User's address
                }
            },
            "institution": {
                "id": incident.institution.id,
                "user": {
                    "name": incident.institution.user.name,  # Akses User's name di Vehicle
                    "address": incident.institution.user.address,  # Akses User's address di Vehicle
                    "avatar": incident.institution.user.avatar,  # Akses User's avatar di Vehicle
                },
            }
        }
    elif incident.status == IncidentStatus.COMPLETED:
        incident_data = {
            "id": incident.id,
            "status": incident.status,
            "description": incident.description,
            "reported_at": incident.reported_at,
            "location": {
                "latitude": incident.latitude,
                "longitude": incident.longitude
            },
            "picture": incident.picture,
            "status": incident.status,
            "resident": {
                "id": incident.resident.id,
                "user": {
                    "id": incident.resident.user.id,  # Akses User dari Resident
                    "name": incident.resident.user.name,  # Akses User's name
                    "avatar": incident.resident.user.avatar  # Akses User's address
                }
            },
            "institution": {
                "id": incident.institution.id,
                "user": {
                    "name": incident.institution.user.name,  # Akses User's name di Vehicle
                    "address": incident.institution.user.address,  # Akses User's address di Vehicle
                    "avatar": incident.institution.user.avatar,  # Akses User's avatar di Vehicle
                },
            }
        }
    elif incident.status == IncidentStatus.REJECTED:
        incident_data = {
            "id": incident.id,
            "status": incident.status,
            "description": incident.description,
            "reported_at": incident.reported_at,
            "location": {
                "latitude": incident.latitude,
                "longitude": incident.longitude
            },
            "picture": incident.picture,
            "status": incident.status,
            "resident": {
                "id": incident.resident.id,
                "user": {
                    "id": incident.resident.user.id,  # Akses User dari Resident
                    "name": incident.resident.user.name,  # Akses User's name
                    "avatar": incident.resident.user.avatar  # Akses User's address
                }
            },
            "institution": {
                "id": incident.institution.id,
                "user": {
                    "name": incident.institution.user.name,  # Akses User's name di Vehicle
                    "address": incident.institution.user.address,  # Akses User's address di Vehicle
                    "avatar": incident.institution.user.avatar,  # Akses User's avatar di Vehicle
                },
            }
        }
    else:
        return jsonify(status=False, message='Status Insiden tidak valid'), 400
        
    # Mengembalikan respons
    return jsonify(
        status=True,
        message='Inseden berhasil dimuat.',
        data=incident_data
    ), 200
# Akhir Ambil Data berdasarkan ID

# Sudah Sampai
@incident_vehicle_route.route('/<int:incident_id>/arrive', methods=['PUT'])
@auth.login_required
def arrive_incident_vehicle(incident_id):
    try:
        # Ambil user berdasarkan data login
        user_id = get_jwt_identity()
        driver_id = Driver.query.filter_by(user_id = user_id).with_entities(Driver.id).scalar()

        # Get incident 
        incident = Incident.query.filter_by(id=incident_id).first()
        if not incident:
            return jsonify({
                'status': False,
                'message': 'Insiden tidak ditemukan.'
            }), 404
        
        # Cek kendaraan darurat milik driver
        incident_vehicle = (
            IncidentVehicle.query
            .join(Vehicle, Vehicle.id == IncidentVehicle.vehicle_id)
            .filter(
                IncidentVehicle.status == IncidentVehicleStatus.ON_ROUTE,
                IncidentVehicle.incident_id == incident_id,
                Vehicle.driver_id == driver_id
            )
            .first()
        )

        if not incident_vehicle:
            return jsonify({
                'status': False,
                'message': 'Kendaraan Insiden tidak ditemukan.'
            }), 404
            
        db.session.begin_nested()
        
        # Perbarui status Inciden Vehicle
        incident_vehicle.status=IncidentVehicleStatus.ARRIVED
        incident_vehicle.arrived_at=get_current_time_in_timezone('Asia/Jakarta') # WIB

        db.session.commit()

        return jsonify({
            'status': True,
            'message': 'Insiden berhasil ditangani',
            'data': {
                    'status': incident_vehicle.status,
                    'arrived_at': incident_vehicle.arrived_at
            }
        }), 200

    except Exception as e:
        # Rollback untuk semua jenis kesalahan
        db.session.rollback()

        # Tangani ValidationError secara spesifik
        if isinstance(e, ValidationError):
            return jsonify({
                'status': False,
                'message': 'Kesalahan validasi',
                'errors': e.messages
            }), 400
        
        return jsonify({
            'status': False,
            'message': f'Terjadi kesalahan: {str(e)}'
        }), 500
# Akhir Sudah Sampai

# Sudah Selesai
@incident_vehicle_route.route('/<int:incident_id>/complete', methods=['PUT'])
@auth.login_required
def complete_incident_vehicle(incident_id):
    try:
         # Ambil user berdasarkan data login
        user_id = get_jwt_identity()
        driver_id = Driver.query.filter_by(user_id = user_id).with_entities(Driver.id).scalar()

        # Get incident 
        incident = Incident.query.filter_by(id=incident_id).first()
        if not incident:
            return jsonify({
                'status': False,
                'message': 'Insiden tidak ditemukan.'
            }), 404
        
        # Cek kendaraan darurat milik driver
        incident_vehicle = (
            IncidentVehicle.query
            .join(Vehicle, Vehicle.id == IncidentVehicle.vehicle_id)
            .filter(
                IncidentVehicle.status == IncidentVehicleStatus.ARRIVED,
                IncidentVehicle.incident_id == incident_id,
                Vehicle.driver_id == driver_id
            )
            .first()
        )

        if not incident_vehicle:
            return jsonify({
                'status': False,
                'message': 'Kendaraan Insiden tidak ditemukan.'
            }), 404
            
        db.session.begin_nested()
        
        # Perbarui status Inciden Vehicle menjadi Completed
        incident_vehicle.status=IncidentVehicleStatus.COMPLETED
        incident_vehicle.completed_at=get_current_time_in_timezone('Asia/Jakarta') # WIB

        db.session.commit()

        return jsonify({
            'status': True,
            'message': 'Insiden berhasil ditangani',
            'data': {
                    'status': incident_vehicle.status,
                    'completed_at': incident_vehicle.completed_at
            }
        }), 200

    except Exception as e:
        # Rollback untuk semua jenis kesalahan
        db.session.rollback()

        # Tangani ValidationError secara spesifik
        if isinstance(e, ValidationError):
            return jsonify({
                'status': False,
                'message': 'Kesalahan validasi',
                'errors': e.messages
            }), 400
        
        return jsonify({
            'status': False,
            'message': f'Terjadi kesalahan: {str(e)}'
        }), 500
# Akhir Sudah Selesai