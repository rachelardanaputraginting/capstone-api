import os
from app.extensions import db, mail
from marshmallow import ValidationError
from flask import Blueprint, request, jsonify, render_template
from werkzeug.security import generate_password_hash
from sqlalchemy.exc import IntegrityError

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
    schema = CreateVehicleSchema(db_session=db.session)

    # Validasi data request
    try:
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify({'success': False, 'errors': err.messages}), 400

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

# Update 
@vehicle_route.route('/<int:vehicle_id>', methods=['PUT'])
@auth.login_required
def update_vehicle(vehicle_id):
    # Get vehicle 
    vehicle = Vehicle.query.get(vehicle_id)

    # Create schema with current vehicle data
    schema = UpdateVehicleSchema(db_session=db.session, vehicle_id=vehicle_id)
    
    try:
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify({'success': False, 'errors': err.messages}), 400
        
    try:
       # Update vehicle data with fallback to existing values
        vehicle.name = data.get('name', vehicle.name)
        vehicle.description = data.get('description', vehicle.description)
        vehicle.institution_id = data.get('institution_id', vehicle.institution_id)
        vehicle.driver_id = data.get('driver_id', vehicle.driver_id)
        vehicle.is_ready = data.get('is_ready', vehicle.is_ready)
        vehicle.picture = data.get('picture', vehicle.picture)

        # Commit changes
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Vehicle updated successfully',
            'data': {
                'vehicle': {
                    'id': vehicle.id,
                    'name': vehicle.name,
                    'description': vehicle.description,
                    'institution_id': vehicle.institution_id,
                    'driver_id': vehicle.driver_id,
                    'is_ready': vehicle.is_ready,
                    'picture': vehicle.picture
                }
            }
        }), 200

    except ValidationError as err:
        db.session.rollback()
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
# End Update 

# Delete
@vehicle_route.route('/<int:vehicle_id>', methods=['DELETE'])
@auth.login_required
def delete_driver(vehicle_id):
    try:
        vehicle_obj = Vehicle.query.filter_by(id=vehicle_id).first()
        if not vehicle_obj:
            return jsonify({'success': False, 'message': 'Vehicle not found'}), 404
        
        # Query driver berdasarkan ID
        vehicle = Vehicle.query.get_or_404(vehicle_id)
        
        # Mulai transaksi
        db.session.begin_nested()

        # Hapus data Driver
        db.session.delete(vehicle)

        # Commit transaksi
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Vehicle deleted successfully.'
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'An error occurred: {str(e)}'
        }), 500
# End Delete