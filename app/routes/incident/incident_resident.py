from app.extensions import db
from marshmallow import ValidationError
from flask import Blueprint, request, jsonify

from utils import auth
from app.models.models import Incident

# schemas
# from app.schemas.incident.create_schema import CreateVehicleSchema
# from app.schemas.incident.update_schema import UpdateVehicleSchema

incident_resident_route = Blueprint('incidents/residents', __name__)

# Ambil Data
@incident_resident_route.route('/', methods=['GET'])
@auth.login_required
def get_incident_resident():
    # Dapatkan parameter kueri penelusuran
    # search_name = request.args.get('name', None)

    # Bangun kuer
    incidents = db.session.query(
        Incident.id.label('incident_id'),
        Incident.description,
        Incident.reported_at,
        Incident.picture,
        Incident.status,
    ).all()  # Gunakan alias di sini

    
    # # Terapkan filter
    # if search_name:
    #     query = query.filter(Incident.name.ilike(f'%{search_name}%'))  # Filter berdasarkan nama driver

    # # Jalankan kueri
    # incidents = query.all()

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