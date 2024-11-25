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
from app.models.models import Vehicle, User, Driver, Institution

# schemas
from app.schemas.vehicle.create_schema import CreateVehicleSchema
from app.schemas.vehicle.update_schema import UpdateVehicleSchema

vehicle_route = Blueprint('institutions/vehicles', __name__)

# Get All
@vehicle_route.route('/', methods=['GET'])
@auth.login_required
def get_vehicles():
    # Get search query parameters
    search_name = request.args.get('name', None)

    # Build the query
    query = db.session.query(
        Vehicle.id.label('vehicle_id'),
        Vehicle.is_ready,
        Vehicle.picture,
        Driver.id.label('driver_id'),
        User.id.label('user_id'),
        User.name.label('driver_name'),
        Institution.id.label('institution_id'),
    ).join(Driver, Vehicle.driver_id == Driver.id) \
     .join(User, Driver.user_id == User.id) \
     .join(Institution, Vehicle.institution_id == Institution.id)

    # Apply filters
    if search_name:
        query = query.filter(User.name.ilike(f'%{search_name}%'))  # Filter by driver name

    # Execute the query
    vehicles = query.all()

    # Prepare the response
    vehicle_data = [
        {
            "vehicle_id": vehicle.vehicle_id,
            "is_ready": vehicle.is_ready,
            "picture": vehicle.picture,
            "driver": {
                "id": vehicle.driver_id,
                "name": vehicle.driver_name,
            },
            "institution": {
                "id": vehicle.institution_id,
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

