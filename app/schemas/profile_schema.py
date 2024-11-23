from marshmallow import Schema, fields, validate, ValidationError
from marshmallow.decorators import validates_schema, validates
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models.models import User, Resident, Driver, Institution

# Base Schema for common user fields
class BaseProfileSchema(Schema):
    name = fields.String(required=False, validate=[validate.Length(min=1, max=50)])
    email = fields.Email(required=False, validate=[validate.Length(max=50)])
    username = fields.String(required=False, validate=[validate.Length(min=1, max=50)])
    address = fields.String(validate=[validate.Length(max=255)])

    def __init__(self, db_session: Session, user_id: int, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db_session = db_session
        self.user_id = user_id
        self.current_user = self.db_session.query(User).get(user_id)

    @validates("email")
    def validate_email_unique(self, email):
        if not self.current_user:
            raise ValidationError("Current user not found")
            
        existing_user = self.db_session.query(User).filter(
            and_(User.email == email, User.id != self.user_id)
        ).first()
        
        if existing_user:
            raise ValidationError("Email is already taken")

    @validates("username")
    def validate_username_unique(self, username):
        if not self.current_user:
            raise ValidationError("Current user not found")
            
        existing_user = self.db_session.query(User).filter(
            and_(User.username == username, User.id != self.user_id)
        ).first()
        
        if existing_user:
            raise ValidationError("Username is already taken")

class ResidentProfileSchema(BaseProfileSchema):
    nik = fields.String(required=False, validate=[validate.Length(equal=16)])
    date_of_birth = fields.Date(required=False)
    place_of_birth = fields.String(required=False, validate=[validate.Length(max=50)])
    gender = fields.String(required=False, validate=validate.OneOf(['MAN', 'WOMEN']))
    phone_number = fields.String(required=False, validate=[validate.Length(max=13)])

    @validates("phone_number")
    def validate_phone_number_unique(self, phone_number):
        if not self.current_user or not self.current_user.resident:
            raise ValidationError("Current resident not found")
            
        existing = self.db_session.query(Resident).filter(
            and_(Resident.phone_number == phone_number, 
                 Resident.user_id != self.user_id)
        ).first()
        
        if existing:
            raise ValidationError("Phone number is already taken")

    @validates("nik")
    def validate_nik_unique(self, nik):
        if not self.current_user or not self.current_user.resident:
            raise ValidationError("Current resident not found")
            
        existing = self.db_session.query(Resident).filter(
            and_(Resident.nik == nik, 
                 Resident.user_id != self.user_id)
        ).first()
        
        if existing:
            raise ValidationError("NIK is already taken")

class DriverProfileSchema(BaseProfileSchema):
    phone_number = fields.String(required=False, validate=[validate.Length(max=13)])
    institution_id = fields.Integer(required=False)

    @validates("phone_number")
    def validate_phone_number_unique(self, phone_number):
        if not self.current_user or not self.current_user.driver:
            raise ValidationError("Current driver not found")
            
        existing = self.db_session.query(Driver).filter(
            and_(Driver.phone_number == phone_number, 
                 Driver.user_id != self.user_id)
        ).first()
        
        if existing:
            raise ValidationError("Phone number is already taken")

    @validates("institution_id")
    def validate_institution(self, institution_id):
        institution = self.db_session.query(Institution).get(institution_id)
        if not institution:
            raise ValidationError("Institution not found")

class InstitutionProfileSchema(BaseProfileSchema):
    description = fields.String(required=False)
    latitude = fields.Float(required=False)
    longitude = fields.Float(required=False)

class AdministrationProfileSchema(BaseProfileSchema):
    pass