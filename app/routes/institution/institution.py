from flask_jwt_extended import get_jwt_identity
from app.extensions import db
from marshmallow import ValidationError
from flask import Blueprint, request, jsonify
from utils import auth
from utils import URL
from utils.datetime import get_current_time_in_timezone
from utils.storage import upload_file_to_gcs, allowed_file
from app.models.models import Institution, User, Vehicle, Driver, Incident, Resident
 
from app.schemas.incident.create_schema import CreateIncidentSchema

institution_route = Blueprint('institutions', __name__)

# Tampilkan semua Insiden
@institution_route.route('/', methods=['GET'])
@auth.login_required
def get_all_institutions():
    # Mendapatkan parameter query 'name' jika ada
    search_name = request.args.get('name', None)

    # Membangun query untuk mendapatkan data institusi yang di-join dengan user
    query = db.session.query(
        Institution.id,
        Institution.description,
        User.id.label('user_id'),
        User.username,
        User.email,
        User.avatar,
        User.name,
        User.address
    ).join(User, Institution.user_id == User.id)

    # Jika ada parameter 'name' pada query, filter berdasarkan nama user
    if search_name:
        query = query.filter(User.name.ilike(f'%{search_name}%'))  # Menggunakan ilike untuk pencarian yang tidak case-sensitive

    # Eksekusi query untuk mengambil data institusi
    institutions = query.all()

    # Menyiapkan data respons, termasuk jumlah kendaraan yang siap (ready)
    institution_data = []
    for institution in institutions:
        # Menghitung jumlah kendaraan yang memiliki is_ready = True
        ready_vehicle_count = db.session.query(Vehicle).filter(
            Vehicle.institution_id == institution.id,
            Vehicle.is_ready == True
        ).count()

        # Menambahkan data institusi beserta jumlah kendaraan yang siap
        institution_data.append({
            "id": institution.id,
            "description": institution.description,
            "user": {
                "id": institution.user_id,
                "username": institution.username,
                "email": institution.email,
                "avatar": institution.avatar,
                "name": institution.name,
                "address": institution.address,
            },
            "ready_vehicle_count": ready_vehicle_count  # Menambahkan jumlah kendaraan yang siap
        })

    # Mengembalikan respons dengan data institusi yang sudah difilter dan jumlah kendaraan yang siap
    return jsonify(
        status=True,
        message='Data loaded successfully.',
        data=institution_data
    ), 200
# Akhir Tampilkan semua Insiden

# Tampilkan Instansi berdasarkan ID
@institution_route.route('/<int:institution_id>', methods=['GET'])
@auth.login_required
def get_institution_by_id(institution_id):
    # Kueri untuk mendapatkan data instansi berdasarkan ID
    institution = db.session.query(
        Institution.id,
        User.id.label('user_id'),
        User.username,
        User.avatar,
        User.address,
        User.name,
        Institution.latitude,
        Institution.longitude,
        Institution.description
    ).join(User, Institution.user_id == User.id) \
        .filter(Institution.id == institution_id) \
        .first()

    # Jika data tidak ditemukan
    if not institution:
        return jsonify({
            'status': False,
            'message': 'Instansi tidak ditemukan.'
        }), 404

    # Cek ketersediaan kendaraan siap pakai
    ready_vehicle_count = db.session.query(Vehicle).filter(
        Vehicle.institution_id == institution.id,
        Vehicle.is_ready == True
    ).count()

    # Status instansi: aktif jika ada kendaraan yang siap pakai, tidak aktif jika tidak ada.
    institution_status = "Tersedia" if ready_vehicle_count > 0 else "Kosong"

    # Menyiapkan data instansi
    institution_data = {
        "id": institution.id,
        "username": institution.username,
        "address": institution.address,
        "avatar": institution.avatar,
        "name": institution.name,
        "latitude": institution.latitude,
        "longitude": institution.longitude,
        "description": institution.description,
        "status": institution_status
    }

    # Kueri Kendaraan berdasarkan institution_id dan User
    vehicles = db.session.query(
        Vehicle.id,
        Vehicle.name,
        Vehicle.description,
        Vehicle.is_ready,
        User.id.label('driver_id'),
        User.name.label('driver_name')
    ).join(Driver, Driver.id == Vehicle.driver_id) \
     .join(User, User.id == Driver.user_id) \
     .filter(Vehicle.institution_id == institution_id) \
     .all()

    # Menyiapkan data kendaraan
    vehicle_data = [
        {
            "id": vehicle.id,
            "name": vehicle.name,
            "description": vehicle.description,
            "is_ready": vehicle.is_ready,
            "driver": {
                "id": vehicle.driver_id,
                "name": vehicle.driver_name,
            }
        }
        for vehicle in vehicles
    ]

    # Menggabungkan data kendaraan ke dalam data instansi
    institution_data["vehicles"] = vehicle_data

    # Mengembalikan respons
    return jsonify(
        status=True,
        message='Rincian Instansi berhasil dimuat.',
        data=institution_data
    ), 200
# Akhir Tampilkan Instansi berdasarkan ID

@institution_route.route('/<int:institution_id>/incidents', methods=['POST'])
@auth.login_required
def add_incident(institution_id):
    try:
        # Ambil user berdasarkan data login
        user_id = get_jwt_identity()
        resident = Resident.query.filter_by(user_id=user_id).first()
        
        if not resident:
            return jsonify({
                'status': False,
                'message': 'Masyarakat tidak ditemukan'
            }), 404

        # Handle file upload terlebih dahulu
        if 'picture' not in request.files:
            return jsonify({
                'status': False,
                'message': 'Gambar wajib diunggah'
            }), 400

        file = request.files['picture']
        if file.filename == '':
            return jsonify({
                'status': False,
                'message': 'Tidak ada file yang dipilih'
            }), 400

        # Validate file type
        if not allowed_file(file.filename):
            return jsonify({
                'status': False,
                'message': 'Format file tidak didukung. Gunakan jpg, jpeg atau png.'
            }), 400

        # Prepare data for schema validation
        data = {
            'description': request.form.get('description'),
            'institution_id': institution_id,
            'resident_id': resident.id,
            'latitude': request.form.get('latitude'),
            'longitude': request.form.get('longitude')
        }

        # Validate data using schema
        schema = CreateIncidentSchema(db_session=db.session)
        validated_data = schema.load(data)

        # Upload file to GCS
        upload_result = upload_file_to_gcs(file, directory='incidents')
        if not upload_result['status']:
            return jsonify({
                'status': False,
                'message': 'Gagal mengunggah gambar'
            }), 500

        # Create new incident
        new_incident = Incident(
            institution_id=institution_id,
            resident_id=resident.id,
            description=validated_data['description'],
            latitude=validated_data['latitude'],
            longitude=validated_data['longitude'],
            picture=upload_result['url'],
            reported_at=get_current_time_in_timezone('Asia/Jakarta')
        )

        db.session.add(new_incident)
        db.session.commit()

        return jsonify({
            'status': True,
            'message': 'Laporan berhasil dibuat',
            'data': {
                'id': new_incident.id,
                'institution_id': new_incident.institution_id,
                'resident_id': new_incident.resident_id,
                'description': new_incident.description,
                'latitude': str(new_incident.latitude),
                'longitude': str(new_incident.longitude),
                'picture': new_incident.picture,
                'reported_at': new_incident.reported_at.isoformat()
            }
        }), 201

    except ValidationError as err:
        return jsonify({
            'status': False,
            'message': 'Validasi gagal',
            'errors': err.messages
        }), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': False,
            'message': f'Terjadi kesalahan: {str(e)}'
        }), 500