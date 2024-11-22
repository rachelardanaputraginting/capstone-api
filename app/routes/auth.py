import os
import random
from datetime import datetime
from flask import Blueprint, request, jsonify, render_template
from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash
from sqlalchemy.exc import IntegrityError
from marshmallow import ValidationError
from itsdangerous import URLSafeTimedSerializer
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from utils.datetime import get_current_time_in_timezone

from app.extensions import db, mail
from flask_mail import Message
from app.models.models import Role, User, Resident, Institution
from app.schemas.register_schema import ResidentRegistrationSchema, InstitutionRegistrationSchema

auth = Blueprint('auth', __name__)

# Register User
@auth.route('/register', methods=['POST'])
def register():
    role = request.json.get('role')

    # Pilih schema sesuai dengan role
    if role == 'resident':
        schema = ResidentRegistrationSchema(db_session=db.session)
    elif role == 'institution':
        schema = InstitutionRegistrationSchema(db_session=db.session)
    else:
        return jsonify({'success': False, 'message': 'Invalid role specified'}), 400

    # Validasi data request
    try:
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify({'success': False, 'errors': err.messages}), 400

    # Buat role user
    role_obj = Role.query.filter_by(name=role).first()
    if not role_obj:
        return jsonify({'success': False, 'message': 'Role not found'}), 404

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

        # Simpan semua perubahan ke database
        db.session.commit()

        # Generate token
        access_token = create_access_token(identity=new_user.id)
        
        send_email_verify(new_user)

        return jsonify({
            'success': True,
            'message': 'User registered successfully.',
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
        return jsonify({'success': False, 'message': 'Registration failed due to a database constraint'}), 500
# End Register User

# Send Email Verification
def send_email_verify(user) :
    token = generate_verify_token(user.email)
    msg = Message(
        subject="Verify Email Address",
        recipients=[user.email],
        sender=os.getenv('MAIL_USERNAME'),
        html=render_template('verify_email.html', token=token, name=user.name)
    )
    mail.send(msg)
# End Send Email Verification

# Verify Email
@auth.route('/verify/<token>', methods=['GET'])
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


# Generate Verify Token
def generate_verify_token(email) :
    secret_key = os.getenv('SECRET_KEY') 
    serializer = URLSafeTimedSerializer(secret_key)
    return serializer.dumps(email, salt='salt_key')
# End Generate Verify Token

# Check Verify Token
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
# End CHeck Verify Token
