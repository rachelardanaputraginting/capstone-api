from app.extensions import db, mail
from flask import Blueprint, request, jsonify
from utils import auth
from app.models.models import Institution, User, Vehicle

institution_route = Blueprint('institutions', __name__)

# Get All
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
# End Get All 

# Create 
def add_institution():
    return "Halo"
#End Create