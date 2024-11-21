import random
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash
from sqlalchemy.exc import IntegrityError
from marshmallow import ValidationError

from app.extensions import db
from app.models.models import Role, User, Resident, Institution
from app.schemas.register_schema import ResidentRegistrationSchema, InstitutionRegistrationSchema

auth = Blueprint('auth', __name__)

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
