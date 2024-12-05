from flask_jwt_extended import get_jwt_identity
from app.extensions import db
from marshmallow import ValidationError
from flask import Blueprint, request, jsonify
from utils.datetime import get_current_time_in_timezone
from utils import auth
from app.models.models import Incident, IncidentStatus, Institution, IncidentVehicle, IncidentVehicleStatus, Vehicle

from app.schemas.incident.handle_schema import HandleIncidentSchema

incident_institution_route = Blueprint('incidents/institutions', __name__)

# Ambil Data
@incident_institution_route.route('/', methods=['GET'])
@auth.login_required
def get_incident_institution():
    # Ambil user berdasarkan data login
    user_id = get_jwt_identity()
    institution_id = Institution.query.filter_by(user_id = user_id).with_entities(Institution.id).scalar()
    
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
        institution_id = institution_id
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
@incident_institution_route.route('/<int:incident_id>', methods=['GET'])
@auth.login_required
def get_incident_institution_by_id(incident_id):
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
                    "name": incident.institution.user.name,  # Akses User's name di Institution
                    "address": incident.institution.user.address,  # Akses User's address di Institution
                    "avatar": incident.institution.user.avatar,  # Akses User's avatar di Institution
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
                    "name": incident.institution.user.name,  # Akses User's name di Institution
                    "address": incident.institution.user.address,  # Akses User's address di Institution
                    "avatar": incident.institution.user.avatar,  # Akses User's avatar di Institution
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
                    "name": incident.institution.user.name,  # Akses User's name di Institution
                    "address": incident.institution.user.address,  # Akses User's address di Institution
                    "avatar": incident.institution.user.avatar,  # Akses User's avatar di Institution
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
                    "name": incident.institution.user.name,  # Akses User's name di Institution
                    "address": incident.institution.user.address,  # Akses User's address di Institution
                    "avatar": incident.institution.user.avatar,  # Akses User's avatar di Institution
                },
            }
        }
    else:
        return jsonify(status=False, message='Status Insiden tidak valid'), 400
        
    # Mengembalikan respons
    return jsonify(
        status=True,
        message='Data berhasil dimuat.',
        data=incident_data
    ), 200
# Akhir Ambil Data berdasarkan ID

# Tangani Insiden
@incident_institution_route.route('/<int:incident_id>/handle', methods=['PUT'])
@auth.login_required
def handle_incident(incident_id):
    try:
        # Buat skema dengan data kendaraan saat ini
        schema = HandleIncidentSchema(db_session=db.session, incident_id=incident_id)

        # Validasi permintaan data
        try:
            data = schema.load(request.json)
        except ValidationError as err:
            return jsonify({
                'status': False,
                'message': 'Validasi data gagal',
                'errors': err.messages
            }), 400

        # Get incident 
        incident = Incident.query.filter_by(id=incident_id).first()
        if not incident:
            return jsonify({
                'status': False,
                'message': 'Insiden tidak ditemukan.'
            }), 404
            
        db.session.begin_nested()

        # Perbarui status incident
        incident.status = IncidentStatus.HANDLED 
        incident.handle_at = get_current_time_in_timezone('Asia/Jakarta')

        incident_vehicles_list = []  # Menyimpan kendaraan untuk respon

        # Proses kendaraan yang terpilih
        for incident_vehicle_data in data['vehicles']:
            vehicle = Vehicle.query.filter_by(id=incident_vehicle_data['vehicle_id']).first()
            
            if not vehicle:
                return jsonify({
                    'status': False,
                    'message': f"Kendaraan dengan ID {incident_vehicle_data['vehicle_id']} tidak ditemukan."
                }), 404
            
            # Ubah status kendaraan menjadi tidak siap (false)
            vehicle.is_ready = False

            new_incident_vehicle = IncidentVehicle(
                incident_id=incident.id,
                vehicle_id=vehicle.id,
                status=IncidentVehicleStatus.ON_ROUTE,
                assigned_at=get_current_time_in_timezone('Asia/Jakarta')
            )

            # Tambahkan kendaraan baru ke tabel incident_vehicles
            db.session.add(new_incident_vehicle)
            db.session.add(vehicle)

            incident_vehicles_list.append({
                'vehicle_id': vehicle.id,
                'status': 'ON_ROUTE',
                'assigned_at': new_incident_vehicle.assigned_at
            })

        db.session.commit()

        return jsonify({
            'status': True,
            'message': 'Insiden berhasil ditangani',
            'data': {
                'incident': {
                    'id': incident.id,
                    'status': incident.status,
                    'handle_at': incident.handle_at
                },
                'vehicles': [
                    {
                        'vehicle_id': vehicle_data['vehicle_id'],
                        'is_ready': False  # Menunjukkan kendaraan sedang tidak siap
                    }
                    for vehicle_data in data['vehicles']
                ],
                'incident_vehicles': incident_vehicles_list,
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': False,
            'message': f'Terjadi kesalahan: {str(e)}'
        }), 500
# Akhir Tangani Insiden

# Selesai Insiden
@incident_institution_route.route('/<int:incident_id>/complete', methods=['PUT'])
@auth.login_required
def complete_incident(incident_id):
    try:
        # Get incident 
        incident = Incident.query.filter_by(id=incident_id).first()
        if not incident:
            return jsonify({
                'status': False,
                'message': 'Insiden tidak ditemukan.'
            }), 404
        
        # Ambil semua kendaraan yang terkait dengan incident dan pastikan semua sudah selesai
        incident_vehicles = IncidentVehicle.query.filter_by(incident_id=incident_id).all()
        for ivd in incident_vehicles:
            if ivd.status != IncidentStatus.COMPLETED:
                return jsonify({
                    'status': False,
                    'message': 'Kendaraan ada yang belum kembali, atau Insiden belum selesai ditangani.'
                }), 400  # Gunakan 400 karena ini adalah kesalahan validasi

        # Perbarui status incident
        incident.status = IncidentStatus.COMPLETED 
        incident.completed_at = get_current_time_in_timezone('Asia/Jakarta')

         # Perbarui status kendaraan yang terlibat dalam insiden menjadi "AVAILABLE"
        for ivd in incident_vehicles:
            ivd.vehicle.is_ready = True  # Status kendaraan kembali ke "available" atau "ready"

        db.session.commit()

        return jsonify({
            'status': True,
            'message': 'Insiden selesai ditangani',
            'data': {
                'incident': {
                    'id': incident.id,
                    'status': incident.status,
                    'completed_at': incident.completed_at
                },
                'vehicles': [
                    {
                        'id': ivd.vehicle.id,
                        'name': ivd.vehicle.name,
                        'is_ready': ivd.vehicle.is_ready  # Status kendaraan
                    }
                    for ivd in incident_vehicles
                ]
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': False,
            'message': f'Terjadi kesalahan: {str(e)}'
        }), 500
# Akhir Selesai Insiden