import os
import secrets

from flask import request, jsonify, Blueprint, render_template
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jti, get_jwt
from werkzeug.security import check_password_hash, generate_password_hash
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Message
from datetime import datetime, timedelta
import random

from app.extensions import db, mail
from app.models.models import Role, User, Resident, Institution
# from app.models.LoginLog import LoginLog
from app.models.reset_password import ResetPassword
from utils import auth

from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from app.schemas.register_schema import ResidentRegistrationSchema, InstitutionRegistrationSchema

from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

auth = Blueprint('auth', __name__)

# Register
@auth.route('/register', methods=['POST'])
def register():
    # Get the role from the request
    role = request.json.get('role')
    
    # Select appropriate schema based on role
    if role == 'resident':
        schema = ResidentRegistrationSchema()
    elif role == 'institution':
        schema = InstitutionRegistrationSchema()
    else:
        return jsonify({
            'success': False, 
            'message': 'Invalid role specified'
        }), 400

    # Validate the request data
    try:
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify({
            'success': False,
            'message': 'Validation error',
            'errors': err.messages
        }), 400

    # Check if a user with the given email or username already exists
    existing_user = User.query.filter(
        (User.email == data['email']) | (User.username == data['username'])
    ).first()

    if existing_user:
        return jsonify({
            'success': False,
            'message': 'Email or username already exists'
        }), 400

    try:
        # Find the appropriate role
        role_obj = Role.query.filter_by(name=role).first()
        if not role_obj:
            return jsonify({
                'success': False,
                'message': 'Role not found'
            }), 404

        # Create the user
        new_user = User(
            name=data['name'],
            email=data['email'],
            address=data['address'],
            username=data['username'],
            password=generate_password_hash(data['password'])
        )

        db.session.add(new_user)
        db.session.flush()
        
        # Attach the role to the user
        # new_user.roles.append(role_obj)
        print(new_user.id)
        # Additional details based on role
        if role == 'resident':
            resident = Resident(
                user_id=new_user.id,
                nik=data['nik'],
                date_of_birth=data['date_of_birth'],
                place_of_birth=data['place_of_birth'],
                gender=data['gender'],
                phone_number=data['phone_number']
            )
            print(resident)
            db.session.add(resident)
        
        elif role == 'institution':
            institution = Institution(
                user_id=new_user.id,
                service_id=data['service_id'],
                description=data['description'],
                latitude=data['latitude'],
                longitude=data['longitude']
            )
            db.session.add(institution)

        # Generate email verification pin
        verification_pin = str(random.randint(100000, 999999))
        
        # Send verification email
        # send_verification_email(new_user.email, verification_pin)

        # Commit database transaction
        db.session.commit()

        # Create access token
        access_token = create_access_token(identity=new_user.id)

        return jsonify({
            'success': True,
            'message': 'User registered successfully. Please check your email for verification.',
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
        return jsonify({
            'success': False,
            'message': 'Registration failed due to a database constraint'
        }), 500
# End Register