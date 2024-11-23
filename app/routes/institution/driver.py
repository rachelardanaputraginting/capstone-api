from app.extensions import db, mail
from flask import Blueprint, request, jsonify
from utils import auth
from app.models.models import Driver, User

driver_route = Blueprint('institutions/drivers', __name__)

# Get All
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
        message='Data loaded successfully.',
        data=driver_data
    ), 200

# End Get All 