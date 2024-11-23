from marshmallow import Schema, fields, validate, ValidationError
from marshmallow.decorators import validates_schema, validates
from sqlalchemy.orm import Session
from app.models.models import User, Resident, Institution, Driver

class ResidentRegistrationSchema(Schema):
    name = fields.String(required=True, validate=[validate.Length(min=1, max=50)])
    email = fields.Email(required=True, validate=[validate.Length(max=50)])
    username = fields.String(required=True, validate=[validate.Length(min=1, max=30)])
    address = fields.String(allow_none=True, validate=[validate.Length(max=100)])
    password = fields.String(required=True, validate=[validate.Length(min=8)])
    password_confirmation = fields.String(required=True)
    role = fields.String(required=True, validate=validate.OneOf(['resident']))

    # Resident-specific fields
    nik = fields.String(required=True, validate=[validate.Length(equal=16)])
    date_of_birth = fields.Date(required=True)
    place_of_birth = fields.String(required=True)
    gender = fields.String(required=True, validate=validate.OneOf(['MAN', 'WOMEN']))
    phone_number = fields.String(required=True)

    def __init__(self, db_session: Session, *args, **kwargs):
        """Initialize schema with a database session."""
        super().__init__(*args, **kwargs)
        self.db_session = db_session

    @validates("email")
    def validate_email_unique(self, email):
        if self.db_session.query(User).filter(User.email == email).first():
            raise ValidationError("Email is already taken.")

    @validates("username")
    def validate_username_unique(self, username):
        if self.db_session.query(User).filter(User.username == username).first():
            raise ValidationError("Username is already taken.")

    @validates("nik")
    def validate_nik_unique(self, nik):
        if self.db_session.query(Resident).filter_by(nik=nik).first():
            raise ValidationError("NIK is already taken.")
        
    @validates("phone_number")
    def validate_nik_unique(self, phone_number):
        if self.db_session.query(Resident).filter_by(phone_number=phone_number).first():
            raise ValidationError("Number Phone is already taken.")
        elif self.db_session.query(Driver).filter_by(phone_number=phone_number).first():
            raise ValidationError("Number Phone is already taken.")

    @validates_schema
    def validate_passwords_match(self, data, **kwargs):
        if data.get('password') != data.get('password_confirmation'):
            raise ValidationError('Passwords do not match', 'password_confirmation')


class InstitutionRegistrationSchema(Schema):
    name = fields.String(required=True, validate=[validate.Length(min=1, max=255)])
    email = fields.Email(required=True, validate=[validate.Length(max=255)])
    username = fields.String(required=True, validate=[validate.Length(min=1, max=255)])
    address = fields.String(required=True, validate=[validate.Length(max=500)])
    password = fields.String(required=True, validate=[validate.Length(min=8)])
    password_confirmation = fields.String(required=True)
    role = fields.String(required=True, validate=validate.OneOf(['institution']))

    # Institution-specific fields
    description = fields.String(required=True)
    latitude = fields.Float(required=True)
    longitude = fields.Float(required=True)

    def __init__(self, db_session: Session, *args, **kwargs):
        """Initialize schema with a database session."""
        super().__init__(*args, **kwargs)
        self.db_session = db_session

    @validates("email")
    def validate_email_unique(self, email):
        if self.db_session.query(User).filter(User.email == email).first():
            raise ValidationError("Email is already taken.")

    @validates("username")
    def validate_username_unique(self, username):
        if self.db_session.query(User).filter(User.username == username).first():
            raise ValidationError("Username is already taken.")

    @validates_schema
    def validate_passwords_match(self, data, **kwargs):
        if data.get('password') != data.get('password_confirmation'):
            raise ValidationError('Passwords do not match', 'password_confirmation')
