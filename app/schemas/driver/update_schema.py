from marshmallow import Schema, fields, validate, ValidationError
from marshmallow.decorators import validates_schema, validates
from sqlalchemy.orm import Session
from app.models.models import User, Driver, Institution, Resident
from sqlalchemy import and_, not_

class UpdateDriverSchema(Schema):
    name = fields.String(required=True, validate=[validate.Length(min=1, max=255)])
    email = fields.Email(required=True, validate=[validate.Length(max=255)])
    username = fields.String(required=True, validate=[validate.Length(min=1, max=255)])
    address = fields.String(required=True, validate=[validate.Length(max=500)])
    password = fields.String(validate=[validate.Length(min=8)])
    password_confirmation = fields.String()
    phone_number = fields.String(required=True)
    institution_id = fields.Integer(required=True)

    def __init__(self, db_session: Session, driver_id: int, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db_session = db_session
        self.driver_id = driver_id
        # Get the current driver and user records
        self.current_driver = self.db_session.query(Driver).get(driver_id)
        self.current_user = self.db_session.query(User).get(self.current_driver.user_id) if self.current_driver else None

    @validates("email")
    def validate_email_unique(self, email):
        if not self.current_user:
            raise ValidationError("Current user not found")
            
        # Check if email exists for any other user
        existing_user = self.db_session.query(User).filter(
            and_(
                User.email == email,
                User.id != self.current_user.id
            )
        ).first()
        
        if existing_user:
            raise ValidationError("Email is already taken.")

    @validates("username")
    def validate_username_unique(self, username):
        if not self.current_user:
            raise ValidationError("Current user not found")
            
        # Check if username exists for any other user
        existing_user = self.db_session.query(User).filter(
            and_(
                User.username == username,
                User.id != self.current_user.id
            )
        ).first()
        
        if existing_user:
            raise ValidationError("Username is already taken.")
    
    @validates("phone_number")
    def validate_phone_number_unique(self, phone_number):
        if not self.current_driver:
            raise ValidationError("Current driver not found")
            
        # Check if phone number exists in drivers table (excluding current driver)
        existing_driver = self.db_session.query(Driver).filter(
            and_(
                Driver.phone_number == phone_number,
                Driver.id != self.current_driver.id
            )
        ).first()
        
        if existing_driver:
            raise ValidationError("Phone number is already taken by another driver.")

        # Check if phone number exists in residents table
        existing_resident = self.db_session.query(Resident).filter(
            Resident.phone_number == phone_number
        ).first()
        
        if existing_resident:
            raise ValidationError("Phone number is already taken by a resident.")
    
    @validates('institution_id')
    def validate_institution_id(self, value):
        institution = self.db_session.query(Institution).get(value)
        if not institution:
            raise ValidationError("Institution with the given ID does not exist.")

    @validates_schema
    def validate_passwords_match(self, data, **kwargs):
        if data.get('password'):
            if not data.get('password_confirmation'):
                raise ValidationError('Password confirmation is required when setting a new password.')
            if data['password'] != data['password_confirmation']:
                raise ValidationError('Passwords do not match', 'password_confirmation')