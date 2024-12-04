from flask_jwt_extended import get_jwt_identity
from app.extensions import db
from marshmallow import ValidationError
from flask import Blueprint, request, jsonify
from utils.datetime import get_current_time_in_timezone
from utils import auth
from app.models.models import Incident, IncidentStatus, Institution, IncidentVehicleDriver, IncidentVehicleDriverStatus

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
        message='Laporan Kejadian Darurat berhasil dimuat.',
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
            message='Laporan tidak ditemukan.',
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
        return jsonify(status=False, message='Status Laporan tidak valid'), 400
        
    # Mengembalikan respons
    return jsonify(
        status=True,
        message='Data berhasil dimuat.',
        data=incident_data
    ), 200
# Akhir Ambil Data berdasarkan ID

# Tangani Laporan Kejadian
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
                'message': 'Laporan tidak ditemukan.'
            }), 404
            
        db.session.begin_nested()

        # Perbarui status incident
        incident.status = IncidentStatus.HANDLED 
        incident.handled_at = get_current_time_in_timezone('Asia/Jakarta')
        
        # Tambahkan kendaraan ke incident
        for vehicle_data in data['vehicles']:
            new_incident_vehicle = IncidentVehicleDriver(
                incident_id=incident.id,
                vehicle_id=vehicle_data['vehicle_id'],
                status=IncidentVehicleDriverStatus.ON_ROUTE,
                assigned_at=get_current_time_in_timezone('Asia/Jakarta')
            )
            db.session.add(new_incident_vehicle)

        db.session.commit()

        return jsonify({
            'status': True,
            'message': 'Laporan insiden berhasil ditangani',
            'data': {
                'incident': {
                    'id': incident.id,
                    'status': incident.status,
                    'handled_at': incident.handled_at
                },
                'vehicles': [
                    {
                        'vehicle_id': vehicle_data['vehicle_id'],
                        'status': 'ON_ROUTE',
                        'assigned_at': new_incident_vehicle.assigned_at
                    }
                    for vehicle_data in data['vehicles']
                ]
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': False,
            'message': f'Terjadi kesalahan: {str(e)}'
        }), 500
# Akhir Laporan Kejadian