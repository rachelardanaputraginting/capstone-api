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
from app.models.models import Driver, User, Role, UserRole, Institution

# schemas
from app.schemas.driver.create_schema import CreateDriverSchema

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

# Create
@driver_route.route('/', methods=['POST'])
@auth.login_required
def add_driver():
    role = "driver"
    institution = request.json.get('institution_id')
    
    schema = CreateDriverSchema(db_session=db.session)

    # Validasi data request
    try:
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify({'success': False, 'errors': err.messages}), 400

    # Buat role user
    role_obj = Role.query.filter_by(name=role).first()
    if not role_obj:
        return jsonify({'success': False, 'message': 'Role not found'}), 404\
            
    institution_obj = Institution.query.filter_by(id=institution).first()
    if not institution_obj:
        return jsonify({'success': False, 'message': 'Institution not found'}), 404

    # Simpan data user ke database
    try:
        new_user = User(
            name=data['name'],
            email=data['email'],
            username=data['username'],
            password=generate_password_hash(data['password']),
            address=data.get('address'),
        )
        db.session.add(new_user)
        db.session.flush()

        new_driver = Driver(
            institution_id=data['institution_id'],
            user_id=new_user.id,
            phone_number=data['phone_number']
        )
        db.session.add(new_driver)
        
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
            'success': True,
            'message': 'Driver created successfully.',
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
        return jsonify({'success': False, 'message': 'Add Driver failed due to a database constraint'}), 500
# End Create

# Send Email Verification
def send_email_verify(user) :
    token = generate_verify_token(user.email)
    msg = Message(
        subject="Verify Email Address",
        recipients=[user.email],
        sender=os.getenv('MAIL_USERNAME'),
        html=render_template('institution/verify_email.html', token=token, name=user.name)
    )
    mail.send(msg)
# End Send Email Verification

# Generate Verify Token
def generate_verify_token(email) :
    secret_key = os.getenv('SECRET_KEY') 
    serializer = URLSafeTimedSerializer(secret_key)
    return serializer.dumps(email, salt='salt_key')
# End Generate Verify Token