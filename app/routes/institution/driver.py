import os
from app.extensions import db, mail
from marshmallow import ValidationError
from flask import Blueprint, request, jsonify, render_template
from werkzeug.security import generate_password_hash
from flask_jwt_extended import create_access_token
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Message

from utils import auth
from app.models.models import Driver, User, Role, UserRole

# schemas
from app.schemas.driver.create_schema import CreateDriverSchema
from app.schemas.driver.update_schema import UpdateDriverSchema

driver_route = Blueprint('institutions/drivers', __name__)

# Ambil Data
@driver_route.route('/', methods=['GET'])
@auth.login_required
def get_all_drivers():
    # Get the search query parameter, if any
    search_name = request.args.get('name', None)

    # Build the query
    query = db.session.query(
        Driver.id,
        User.id.label('user_id'),
        User.username,
        User.email,
        User.avatar,
        User.name
    ).join(User, Driver.user_id == User.id)

    # If a search name is provided, filter by the user's name
    if search_name:
        query = query.filter(User.name.ilike(f'%{search_name}%'))  # Use ilike for case-insensitive matching

    # Execute the query
    drivers = query.all()

    # Prepare the response
    driver_data = [
        {
            "id": driver.id,
            "user": {
                "id": driver.user_id,
                "username": driver.username,
                "email": driver.email,
                "avatar": driver.avatar,
                "name": driver.name,
            }
        }
        for driver in drivers
    ]

    # Return the response with the filtered driver data
    return jsonify(
        status=True,
        message='Data berhasil dimuat.',
        data=driver_data
    ), 200
# Akhir Ambil Data 

# Ambil Data berdasarkan ID
@driver_route.route('/<int:driver_id>', methods=['GET'])
@auth.login_required
def get_driver_by_id(driver_id):
    # Query untuk mendapatkan data driver berdasarkan ID
    driver = db.session.query(
        Driver.id,
        User.id.label('user_id'),
        User.username,
        User.email,
        User.avatar,
        User.address,
        User.name,
        Driver.phone_number
    ).join(User, Driver.user_id == User.id) \
     .filter(Driver.id == driver_id) \
     .first()

    # Jika data tidak ditemukan
    if not driver:
        return jsonify(
            status=False,
            message='Pengemudi tidak ditemukan.',
            data=None
        ), 404

    # Menyiapkan data untuk respons
    driver_data = {
        "id": driver.id,
        "user": {
            "id": driver.user_id,
            "username": driver.username,
            "email": driver.email,
            "address": driver.address,
            "avatar": driver.avatar,
            "name": driver.name,
        },
        "phone_number": driver.phone_number,
    }

    # Mengembalikan respons
    return jsonify(
        status=True,
        message='Data berhasil dimuat.',
        data=driver_data
    ), 200
# Akhir Ambil Data berdasarkan ID

# Tambah Pengemudi
@driver_route.route('/', methods=['POST'])
@auth.login_required
def add_driver():
    try:
        # Validasi permintaan data
        schema = CreateDriverSchema(db_session=db.session)
        try:
            data = schema.load(request.json)
        except ValidationError as err:
            return jsonify({
                'status': False,
                'message': 'Validasi data gagal',
                'errors': err.messages
            }), 400

        # Buat role user
        role = "driver"
        role_obj = Role.query.filter_by(name=role).first()

        # Simpan data user ke database
        new_user = User(
            name=data['name'],
            email=data['email'],
            username=data['username'],
            password=generate_password_hash(data['password']),
            address=data.get('address'),
        )
        db.session.add(new_user)
        db.session.flush()

        new_driver = Driver(
            institution_id=data['institution_id'],
            user_id=new_user.id,
            phone_number=data['phone_number']
        )
        db.session.add(new_driver)
        
        # Tambahkan role ke tabel pivot `user_roles`
        user_role = UserRole(
            user_id=new_user.id,
            role_id=role_obj.id
        )
        db.session.add(user_role)

        # Simpan semua perubahan ke database
        db.session.commit()

        # Hasilkan token
        access_token = create_access_token(identity=new_user.id)
        
        send_email_verify(new_user)

        return jsonify({
            'status': True,
            'message': 'Pengemudi berhasil dibuat.',
            'user': {
                'id': new_user.id,
                'name': new_user.name,
                'email': new_user.email,
                'username': new_user.username,
                'token': access_token
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
# Akhir Tambah Pengemudi

# Ubah Pengemudi
@driver_route.route('/<int:driver_id>', methods=['PUT'])
@auth.login_required
def update_driver(driver_id):
    try:
        # Membuat dan memvalidasi skema
        schema = UpdateDriverSchema(db_session=db.session, driver_id=driver_id)
        try:
            data = schema.load(request.json)
        except ValidationError as err:
            return jsonify({
                'status': False,
                'message': 'Validasi data gagal',
                'errors': err.messages
            }), 400
            
        # Dapatkan pengemudi dan pengguna terkait
        driver = Driver.query.get(driver_id)
        user = User.query.get(driver.user_id)

        # Begin transaction
        db.session.begin_nested()

        # Ubah user data
        user.name = data['name']
        user.email = data['email']
        user.username = data['username']
        user.address = data['address']

        if data.get('password'):
            user.password = generate_password_hash(data['password'])

        # Ubah driver data
        driver.phone_number = data['phone_number']
        driver.institution_id = data['institution_id']

        # Melakukan perubahan
        db.session.commit()

        return jsonify({
            'status': True,
            'message': 'Pengemudi berhasil diperbarui',
            'data': {
                'user': user.as_dict(),
                'driver': {
                    'id': driver.id,
                    'phone_number': driver.phone_number,
                    'institution_id': driver.institution_id
                }
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
            
        return jsonify(
            status=False,
            message= f'Terjadi kesalahan: {str(e)}'
        ), 500
# Akhir Ubah

# Hapus Pengemudi
@driver_route.route('/<int:driver_id>', methods=['DELETE'])
@auth.login_required
def delete_driver(driver_id):
    try:
        # Query driver berdasarkan ID
        driver = Driver.query.filter_by(id=driver_id).first()
        if not driver:
            return jsonify({
                'status': False,
                'message': 'Pengemudi tidak ditemukan.'
            }), 404
        
        user_id = driver.user_id  # Simpan user_id untuk menghapus data user
        
        # Mulai transaksi
        db.session.begin_nested()

        # Hapus role dari tabel UserRole
        UserRole.query.filter_by(user_id=user_id).delete()

        # Hapus data Driver
        db.session.delete(driver)

        # Hapus data User
        user = User.query.get(user_id)
        if user:
            db.session.delete(user)

        # Commit transaksi
        db.session.commit()

        return jsonify(
            status=True,
            message='Pengemudi berhasil dihapus.'
        ), 200

    except Exception as e:
        db.session.rollback()
        return jsonify(
            status=False,
            message=f'Terjadi kesalahan: {str(e)}'
        ), 500
# Akhir Hapus Pengemudi

# Kirim Email Verifikasi
def send_email_verify(user) :
    token = generate_verify_token(user.email)
    msg = Message(
        subject="Verify Email Address",
        recipients=[user.email],
        sender=os.getenv('MAIL_USERNAME'),
        html=render_template('institution/verify_email.html', token=token, name=user.name)
    )
    mail.send(msg)
# Akhir Kirim Email Verifikasi

# Hasilkan Verifikasi Token
def generate_verify_token(email) :
    secret_key = os.getenv('SECRET_KEY') 
    serializer = URLSafeTimedSerializer(secret_key)
    return serializer.dumps(email, salt='salt_key')
# Akhir Hasilkan Verifikasi Token