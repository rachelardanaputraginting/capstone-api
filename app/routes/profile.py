from flask_jwt_extended import get_jwt_identity
from flask import Blueprint, request, jsonify
from app.extensions import db
from marshmallow import ValidationError

from utils import auth
from app.models.models import User

from app.schemas.profile_schema import ResidentProfileSchema, DriverProfileSchema, InstitutionProfileSchema, AdministrationProfileSchema

user_route = Blueprint('profiles', __name__)

@user_route.route('/', methods=['GET'])
@auth.login_required
def profile_me():
    # Ambil user dari token otentikasi
    user_id = get_jwt_identity()
    current_user = User.query.filter_by(id=user_id).first()
    if not current_user:
        return jsonify({"error": "User not found"}), 404

    # Ambil role user
    roles = [role.name for role in current_user.roles]

    # Respons berdasarkan role
    if "resident" in roles:
        resident = current_user.resident
        if not resident:
            return jsonify({"error": "Resident data not found"}), 404

        response = {
            "id": current_user.id,
            "username": current_user.username,
            "address": current_user.address,
            "name": current_user.name,
            "email": current_user.email,
            "nik": resident.nik,
            "phone_number": resident.phone_number,
            "date_of_birth": resident.date_of_birth.strftime('%Y-%m-%d'),
            "place_of_birth": resident.place_of_birth,
            "gender": resident.gender.value,
        }

    elif "driver" in roles:
        driver = current_user.driver
        if not driver:
            return jsonify({"error": "Driver data not found"}), 404

        response = {
            "id": current_user.id,
            "name": current_user.name,
            "email": current_user.email,
            "address": current_user.address,
            "phone_number": driver.phone_number,
            "institution_id": driver.institution_id,
        }

    elif "institution" in roles:
        institution = current_user.institution
        if not institution:
            return jsonify({"error": "Institution data not found"}), 404

        # print(institution.id)
        response = {
            "id": current_user.id,
            "name": current_user.name,
            "email": current_user.email,
            "address": current_user.address,
            "description": institution.description,
            "location": {
                "latitude": institution.latitude,
                "longitude": institution.longitude,
            },
        }

    elif "administration" in roles:
        response = {
            "id": current_user.id,
            "name": current_user.name,
            "email": current_user.email,
            "address": current_user.address,
            "created_at": current_user.created_at,
        }

    else:
       return jsonify({"error": "User not found"}), 404

    return jsonify(response)

@user_route.route('/update', methods=['PUT'])
@auth.login_required
def update_profile():
    user_id = get_jwt_identity()
    current_user = User.query.filter_by(id=user_id).first()
    
    # Get user's role
    user_role = current_user.roles[0].name if current_user.roles else None
    
    try:
        request_data = request.get_json()
        if not request_data:
            return jsonify({
                'success': False,
                'message': 'No data provided for update'
            }), 400

        # Select appropriate schema based on user role
        if user_role == 'resident':
            schema = ResidentProfileSchema(db_session=db.session, user_id=user_id)
            data = schema.load(request_data)
            
            # Update resident-specific data only if provided
            resident = current_user.resident

            if not resident:
                return jsonify({"error": "Resident data not found"}), 404
            
            for field in ['nik', 'phone_number', 'date_of_birth', 'place_of_birth', 'gender']:
                if field in data:
                    setattr(resident, field, data[field])
            
            db.session.commit()

            response = {
                "id": current_user.id,
                "username": current_user.username,
                "address": current_user.address,
                "name": current_user.name,
                "email": current_user.email,
                "nik": resident.nik,
                "phone_number": resident.phone_number,
                "date_of_birth": resident.date_of_birth.strftime('%Y-%m-%d'),
                "place_of_birth": resident.place_of_birth,
                "gender": resident.gender.value,
            }

        elif user_role == 'driver':
            schema = DriverProfileSchema(db_session=db.session, user_id=user_id)
            data = schema.load(request_data)
            
            driver = current_user.driver
            if not driver:
                return jsonify({"error": "Driver data not found"}), 404
                
            for field in ['phone_number', 'institution_id']:
                if field in data:
                    setattr(driver, field, data[field])
            
            db.session.commit()

            response = {
                "id": current_user.id,
                "name": current_user.name,
                "email": current_user.email,
                "address": current_user.address,
                "phone_number": driver.phone_number,
                "institution_id": driver.institution_id,
            }

        elif user_role == 'institution':
            schema = InstitutionProfileSchema(db_session=db.session, user_id=user_id)
            data = schema.load(request_data)
            
            institution = current_user.institution
            if not institution:
                return jsonify({"error": "Institution data not found"}), 404
                
            for field in ['description', 'latitude', 'longitude']:
                if field in data:
                    setattr(institution, field, data[field])
            
            db.session.commit()

            response = {
                "id": current_user.id,
                "name": current_user.name,
                "email": current_user.email,
                "address": current_user.address,
                "description": institution.description,
                "location": {
                    "latitude": institution.latitude,
                    "longitude": institution.longitude,
                },
            }

        elif user_role == 'administration':
            schema = AdministrationProfileSchema(db_session=db.session, user_id=user_id)
            data = schema.load(request_data)
            # Handle updates to administration profile if needed
            db.session.commit()

            response = {
                "id": current_user.id,
                "name": current_user.name,
                "email": current_user.email,
                "address": current_user.address,
                "created_at": current_user.created_at,
            }
        else:
            return jsonify({'success': False, 'message': 'Invalid user role'}), 400

        # Update common user data only if provided
        for field in ['name', 'email', 'username', 'address']:
            if field in data:
                # Additional validation for empty strings
                if data[field] == "":
                    return jsonify({
                        'success': False,
                        'message': f'{field.capitalize()} cannot be empty'
                    }), 400
                setattr(current_user, field, data[field])

        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Profile updated successfully',
            'data': response
        }), 200

    except ValidationError as err:
        return jsonify({
            'success': False,
            'message': 'Validation error',
            'errors': err.messages
        }), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'An error occurred: {str(e)}'
        }), 500
