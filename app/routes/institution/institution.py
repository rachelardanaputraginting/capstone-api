from flask_jwt_extended import get_jwt_identity
from app.extensions import db
from marshmallow import ValidationError
from flask import Blueprint, request, jsonify
from utils import auth
from utils.datetime import get_current_time_in_timezone
from app.models.models import Institution, User, Vehicle, Driver, Incident, Resident
from utils.Storage import storage_manager
 
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

# Tambah Laporan [Sisi Resident]
@institution_route.route('/<int:institution_id>/incidents', methods=['POST'])
@auth.login_required
def add_incident(institution_id):
    # Ambil user berdasarkan data login
    user_id = get_jwt_identity()
    resident_id = Resident.query.filter_by(user_id = user_id).with_entities(Resident.id).scalar()

     # Simpan data incident ke database
    try:
        schema = CreateIncidentSchema(db_session=db.session)

        # Validasi permintaan data
        try:
            data = schema.load(request.json)
        except ValidationError as err:
            return jsonify({
                'status': False,
                'message': 'Validasi data gagal',
                'errors': err.messages
            }), 400
        
        file = request.get_json()
        image_base64 = file.get('picture')
        
        if not image_base64:
            return jsonify({
                'status': False,
                'message': 'Tidak ada gambar yang disediakan'
            }), 400
        
        # Upload gambar dan dapatkan path
        file_path = storage_manager.uploadFile(image_base64, dir='incidents')
        
        new_incident = Incident(
            institution_id=institution_id,
            resident_id=resident_id,
            description=data['description'],
            latitude=data['latitude'],
            longitude=data['longitude'],
            picture=file_path,
            reported_at=get_current_time_in_timezone('Asia/Jakarta')  # WIB
        )
        db.session.add(new_incident)

        # Simpan semua perubahan ke database
        db.session.commit()

        return jsonify({
            'status': True,
            'message': 'Laporan berhasil dibuat',
            'data': {
                'id': new_incident.id,
                'institution_id': new_incident.institution_id,
                'resident_id': new_incident.resident_id,
                'description': new_incident.description,
                'latitude': new_incident.latitude,
                'longitude': new_incident.longitude,
                'picture': new_incident.picture,
            }
        }), 201

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
        
        # Tangani kesalahan umum
        return jsonify(
            status=False,
            message= f'Terjadi kesalahan: {str(e)}'
        ), 500
# Akhir Tambah Laporan