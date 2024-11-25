import os
from app.extensions import db, mail
from marshmallow import ValidationError
from flask import Blueprint, request, jsonify, render_template
from werkzeug.security import generate_password_hash
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import create_access_token
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Message

from utils import auth
from app.models.models import Vehicle, User, Vehicle, Institution, Driver

# schemas
from app.schemas.vehicle.create_schema import CreateVehicleSchema
from app.schemas.vehicle.update_schema import UpdateVehicleSchema

vehicle_route = Blueprint('institutions/vehicles', __name__)

from sqlalchemy.orm import aliased

# Get All
@vehicle_route.route('/', methods=['GET'])
@auth.login_required
def get_vehicles():
    # Get search query parameters
    search_name = request.args.get('name', None)

    # Create an alias for the User table to avoid conflict
    institution_user = aliased(User)

    # Build the query
    query = db.session.query(
        Vehicle.id.label('vehicle_id'),
        Vehicle.is_ready,
        Vehicle.name,
        Vehicle.description,
        Vehicle.picture,
        Driver.id.label('driver_id'),
        User.name.label('driver_name'),
    ).join(Driver, Vehicle.driver_id == Driver.id) \
     .join(User, Driver.user_id == User.id)  # Use alias here

    # Apply filters
    if search_name:
        query = query.filter(User.name.ilike(f'%{search_name}%'))  # Filter by driver name

    # Execute the query
    vehicles = query.all()

    # Prepare the response
    vehicle_data = [
        {
            "id": vehicle.vehicle_id,
            "name": vehicle.name,
            "description": vehicle.description,
            "is_ready": vehicle.is_ready,
            "picture": vehicle.picture,
            "driver": {
                "id": vehicle.driver_id,
                "name": vehicle.driver_name
            }
        }
        for vehicle in vehicles
    ]

    # Return the response
    return jsonify(
        status=True,
        message='Vehicles loaded successfully.',
        data=vehicle_data
    ), 200
# End Get All

# Create
@vehicle_route.route('/', methods=['POST'])
@auth.login_required
def add_vehicles():
    institution = request.json.get('institution_id')
    driver = request.json.get('driver_id')
    
    schema = CreateVehicleSchema(db_session=db.session)

    # Validasi data request
    try:
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify({'success': False, 'errors': err.messages}), 400
            
    institution_obj = Institution.query.filter_by(id=institution).first()
    if not institution_obj:
        return jsonify({'success': False, 'message': 'Institution not found'}), 404
    
    driver_obj = Institution.query.filter_by(id=institution).first()
    if not driver_obj:
        return jsonify({'success': False, 'message': 'Driver not found'}), 404

    # Simpan data user ke database
    try:
        new_vehicles = Vehicle(
            institution_id=data['institution_id'],
            driver_id=data['driver_id'],
            name=data['name'],
            description=data['description'],
            is_ready=data['is_ready']
        )
        db.session.add(new_vehicles)

        # Simpan semua perubahan ke database
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Vehicle created successfully.',
            'user': {
                'id': new_vehicles.id,
                'institution_id': new_vehicles.institution_id,
                'driver_id': new_vehicles.driver_id,
                'is_ready': new_vehicles.is_ready,
            }
        }), 201

    except IntegrityError:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Add Vehicle failed due to a database constraint'}), 500
# End Create