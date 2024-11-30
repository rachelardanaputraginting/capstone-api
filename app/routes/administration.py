import os
from app.extensions import db, mail
from marshmallow import ValidationError
from flask import Blueprint, request, jsonify, render_template
from werkzeug.security import generate_password_hash
from flask_jwt_extended import create_access_token
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Message

from utils import auth
from app.models.models import User, Role, UserRole, Administration

# schemas
from app.schemas.administration.create_schema import CreateAdministrationSchema
# from app.schemas.administration.update_schema import UpdateDriverSchema

admin_route = Blueprint('administrations', __name__)

# Ambil Data
@admin_route.route('/', methods=['GET'])
@auth.login_required
def get_all_drivers():
    # Dapatkan parameter kueri penelusuran, jika ada
    search_name = request.args.get('name', None)

    # Bangun kueri
    query = db.session.query(
        User.id.label('user_id'),
        User.username,
        User.email,
        User.avatar,
        User.name
     ).join(UserRole).join(Role).filter(Role.name == 'administration')

     # Terapkan filter
    if search_name:
        query = query.filter(User.name.ilike(f'%{search_name}%'))  # Filter berdasarkan nama administration

    # Jalankan kueri
    administrations = query.all()

    # Siapkan data
    admin_data = [
        {
            "id": administration.user_id,
            "username": administration.username,
            "email": administration.email,
            "avatar": administration.avatar,
            "name": administration.name
        }
        for administration in administrations
    ]

    return jsonify(
        status=True,
        message='Data berhasil dimuat.',
        data=admin_data
    ), 200
# Akhir Ambil Data 

# Tambah Admin
@admin_route.route('/', methods=['POST'])
@auth.login_required
def add_driver():
    try:
        # Validasi permintaan data
        schema = CreateAdministrationSchema(db_session=db.session)
        try:
            data = schema.load(request.json)
        except ValidationError as err:
            return jsonify({
                'status': False,
                'message': 'Validasi data gagal',
                'errors': err.messages
            }), 400

        # Buat role user
        role = "administration"
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

        new_admin = Administration(
            user_id=new_user.id
        )
        db.session.add(new_admin)
        
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
            'message': 'Admin berhasil dibuat.',
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
# Akhir Tambah Admin

# Kirim Email Verifikasi
def send_email_verify(user) :
    token = generate_verify_token(user.email)
    msg = Message(
        subject="Verify Email Address",
        recipients=[user.email],
        sender=os.getenv('MAIL_USERNAME'),
        html=render_template('verify_email.html', token=token, name=user.name)
    )
    mail.send(msg)
# Akhir Kirim Email Verifikasi

# Hasilkan Verifikasi Token
def generate_verify_token(email) :
    secret_key = os.getenv('SECRET_KEY') 
    serializer = URLSafeTimedSerializer(secret_key)
    return serializer.dumps(email, salt='salt_key')
# Akhir Hasilkan Verifikasi Token