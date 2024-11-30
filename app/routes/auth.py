import os
import secrets
from flask import Blueprint, request, jsonify, render_template
from flask_jwt_extended import create_access_token, get_jti, get_jwt_identity, get_jwt
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError
from marshmallow import ValidationError
from itsdangerous import URLSafeTimedSerializer
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from utils.datetime import get_current_time_in_timezone
from utils import auth

from app.extensions import db, mail
from flask_mail import Message
from app.models.models import Role, User, Resident, Institution, UserRole
from app.models.login_log import LoginLog
from app.models.reset_password import ResetPassword

# import schemas
from app.schemas.auth.register_schema import ResidentRegistrationSchema, InstitutionRegistrationSchema
from app.schemas.auth.login_schema import LoginSchema
from app.schemas.auth.forgot_password_schema import ForgotPasswordSchema
from app.schemas.auth.reset_password_schema import ResetPasswordSchema

auth_bp = Blueprint('auth', __name__)

# Daftar Pengguna
@auth_bp.route('/register', methods=['POST'])
def register():
    role = request.json.get('role')

    # Pilih schema sesuai dengan role
    if role == 'resident':
        schema = ResidentRegistrationSchema(db_session=db.session)
    elif role == 'institution':
        schema = InstitutionRegistrationSchema(db_session=db.session)
    else:
        return jsonify({'status': False, 'message': 'Role yang dimasukkan tidak valid'}), 400

    # Validasi permintaan data
    try:
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify({
            'status': False,
            'message': 'Validasi data gagal',
            'errors': err.messages
        }), 400

    # Buat role user
    role_obj = Role.query.filter_by(name=role).first()
    if not role_obj:
        return jsonify({'status': False, 'message': 'Role tidak ditemukan'}), 404

    # Simpan data user ke database
    try:
        new_user = User(
            name=data['name'],
            email=data['email'],
            username=data['username'],
            password=generate_password_hash(data['password']),
            address=data.get('address')
        )
        db.session.add(new_user)
        db.session.flush()

        # Tambahkan data spesifik sesuai role
        if role == 'resident':
            new_resident = Resident(
                user_id=new_user.id,
                nik=data['nik'],
                date_of_birth=data['date_of_birth'],
                place_of_birth=data['place_of_birth'],
                gender=data['gender'],
                phone_number=data['phone_number']
            )
            db.session.add(new_resident)
        elif role == 'institution':
            new_institution = Institution(
                user_id=new_user.id,
                description=data['description'],
                latitude=data['latitude'],
                longitude=data['longitude']
            )
            db.session.add(new_institution)
        
         # Tambahkan role ke tabel pivot `user_roles`
        user_role = UserRole(
            user_id=new_user.id,
            role_id=role_obj.id
        )
        db.session.add(user_role)

        # Simpan semua perubahan ke database
        db.session.commit()

        # Generate token
        access_token = create_access_token(identity=new_user.id)
        
        send_email_verify(new_user)

        return jsonify({
            'status': True,
            'message': 'Pengguna berhasil terdaftar.',
            'user': {
                'id': new_user.id,
                'name': new_user.name,
                'email': new_user.email,
                'username': new_user.username,
                'token': access_token
            }
        }), 201

    except IntegrityError:
        db.session.rollback()
        return jsonify({'status': False, 'message': 'Pendaftaran gagal karena kendala basis data'}), 500
# Akhir Daftar Pengguna

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

# Kirim Email Lupa Kata Sandi
def send_forgot_password(user, reset_token):
    # URL untuk aplikasi mobile
    app_link = f"instahelp://reset-password?token={reset_token}"

    # URL fallback ke web jika aplikasi tidak terinstal
    # web_link = f"https://instahelp.com/reset-password?token={reset_token}"

    msg = Message(
        subject="Forgot Password",
        recipients=[user.email],
        sender=os.getenv('MAIL_USERNAME'),
        html=render_template(
            'forgot_password.html',
            name=user.name,
            app_link=app_link,
            # web_link=web_link
        )
    )
    mail.send(msg)
# Akhir Kirim Email Lupa Kata Sandi

# Verifikasi Email
@auth_bp.route('/verify/<token>', methods=['GET'])
def verify_email(token):
    try:
        email = verify_token(token)
        if not email:
            return render_template('verify_expired.html'), 419
            
        user = db.session.query(User).filter_by(email=email).one()
        
        if user.email_verified_at:
            return render_template('verify_already.html'), 200
        
        user.email_verified_at = get_current_time_in_timezone('Asia/Jakarta')  # WIB
        db.session.commit()
        
        return render_template('verify_success.html'), 200
        
    except NoResultFound:
        return render_template('verify_invalid.html'), 404
    except MultipleResultsFound:
        return render_template('verify_invalid.html'), 500
    except Exception as e:
        return render_template('verify_expired.html'), 419
# Akhir Verifikasi Email

# Masuk
@auth_bp.route('/login', methods=['POST'])
def login():
    # Masuk ke LoginSchema untuk validasi
    schema = LoginSchema()
    
    # Validasi permintaan data
    try:
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify({
            'status': False,
            'message': 'Validasi data gagal',
            'errors': err.messages
        }), 400
        
    email = data['email']
    password = data['password']

    user = User.query.filter_by(email=email).first()

    if user is not None and check_password_hash(user.password, str(password)):
        if user.email_verified_at is None:
            return jsonify(
                status=False,
                message="Please verify your email before logging in."
            ), 400
        
        # Ubah user.id menjadi string untuk menghindari kesalahan “Subjek harus berupa string”
        access_token = create_access_token(identity=str(user.id), fresh=True)
        
        # Membuat Catatan Masuk
        jti = get_jti(access_token)
        try:
            login_log = LoginLog(jti)
        except Exception as e:
            return jsonify(
                status=False,
                message="Berhasil masuk tetapi gagal membuat log. Silakan coba lagi."
            ), 500
        
        response = jsonify(
            status=True,
            message="Anda telah berhasil masuk.",
            data={
                "access_token": access_token
            }
        )
        return response, 200
    else:
        return jsonify(
            status=False,
            message="Gagal masuk. Silakan periksa kredensial Anda dan coba lagi."
        ), 401
# Akhir Masuk

# Data Saya
@auth_bp.route('/me', methods=['GET'])
@auth.login_required
def me():
    try:
        # Ambil ID dari JWT
        user_id = get_jwt_identity()
        if not user_id:
            return jsonify({
                "status": False,
                "message": "Authorization token is invalid or missing user identity."
            }), 401

        # Cari user berdasarkan ID
        user = User.query.filter_by(id=user_id).first()

        if not user:
            return jsonify({
                "status": False,
                "message": "User not found. Please ensure the user exists."
            }), 404

        # Berikan respons jika user ditemukan
        return jsonify({
            "status": True,
            "message": "Data loaded successfully.",
            "data": user.as_dict()
        }), 200

    except Exception as e:
        return jsonify({
        "status": False,
            "message": "An unexpected error occurred.",
            "error": str(e)
        }), 500
# Akhir Data Saya

# Keluar
@auth_bp.route('/logout', methods=['POST'])
@auth.login_required
def logout():
    try:
        # Ambil token identifier dari JWT
        token_identifier = get_jwt()['jti']

        # Cari log berdasarkan token
        log = LoginLog.query.filter_by(token_identifier=token_identifier).first()

        if log is None:
            return jsonify(
                status=False,
                message="Gagal keluar. Tidak ditemukan sesi aktif untuk token ini."
            ), 400

        # Hapus log / tandai logout
        log.destroy()  # Pastikan `destroy` method menangani logika delete dengan benar.

        return jsonify(
            status=True,
            message="Successfully logged out."
        ), 200

    except Exception as e:
        # Log the error for debugging purposes
        print(f"Error during logout: {e}")

        return jsonify(
            status=False,
            message="An error occurred during logout. Please try again later."
        ), 500
# Akhir Keluar

# Lupa Kata Sandi
@auth_bp.route('/forgot-password', methods=['POST'])
def forgotPassword():
    schema = ForgotPasswordSchema()
    
    # Validasi permintaan data
    try:
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify({
            'status': False,
            'message': 'Validasi data gagal',
            'errors': err.messages
        }), 400

    email = data['email']
    user = User.query.filter_by(email=email).first()

    if user:
        reset_token = secrets.token_hex(16)  # Hasilkan token
        reset_entry = ResetPassword(email=email, reset_token=reset_token)  # Simpan token di database
        db.session.add(reset_entry)
        db.session.commit()
        
        send_forgot_password(user, reset_token)

        return jsonify(
            status=True,
            message="Email pengaturan ulang kata sandi telah berhasil dikirim.",
            data={"reset_token": reset_token}
        ), 200

    return jsonify(
        status=False,
        message="Akun tidak ditemukan untuk email yang diberikan."
    ), 400
# Akhir Lupa Kata Sandi

# Atur Ulang Password
@auth_bp.route('/reset-password/<token>', methods=['POST'])
def resetPassword(token):
    schema = ResetPasswordSchema()
    
    # Validasi permintaan data
    try:
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify({
            'status': False,
            'message': 'Validasi data gagal',
            'errors': err.messages
        }), 400

    rp = ResetPassword.query.filter_by(reset_token=token).first()

    if rp:
        password = data['password']
        user = User.query.filter_by(email=rp.email).first()

        if user:
            # Ubah kata sandi
            user.password = generate_password_hash(password.strip())
            db.session.commit()

            # Hapus token reset dari database
            db.session.delete(rp)
            db.session.commit()

            return jsonify(
                status=True,
                message='Kata sandi berhasil diubah.'
            ), 200

    return jsonify(
        status=False,
        message='Token tidak valid.'
    ), 400
# Akhir Atur Ulang Kata Sandi

# Hasilkan Token Verifikasi
def generate_verify_token(email) :
    secret_key = os.getenv('SECRET_KEY') 
    serializer = URLSafeTimedSerializer(secret_key)
    return serializer.dumps(email, salt='salt_key')
# Akhir Hasilkan Token Verifikasi

# Periksa Verifikasi Token
def verify_token(token, expiration=3600):
    secret_key = os.getenv('SECRET_KEY')
    serializer = URLSafeTimedSerializer(secret_key)
    try:
        email = serializer.loads(
            token,
            salt='salt_key',
            max_age=expiration
        )
        return email
    except:
        return None
# Akhir Periksa Verifikasi Token
