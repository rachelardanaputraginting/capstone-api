from marshmallow import Schema, fields, validate, ValidationError
from marshmallow.decorators import validates_schema, validates
from sqlalchemy.orm import Session
from app.models.models import User, Driver, Institution

class UpdateDriverSchema(Schema):
    name = fields.String(required=True, validate=[validate.Length(min=1, max=255)])
    email = fields.Email(required=True, validate=[validate.Length(max=255)])
    username = fields.String(required=True, validate=[validate.Length(min=1, max=255)])
    address = fields.String(required=True, validate=[validate.Length(max=500)])
    password = fields.String(validate=[validate.Length(min=8)])
    password_confirmation = fields.String()
    phone_number = fields.String(required=True)
    institution_id = fields.Integer(required=True)

    def __init__(self, db_session: Session, user_id: int, *args, **kwargs):
        """Initialize schema with a database session and user_id for updating."""
        super().__init__(*args, **kwargs)
        self.db_session = db_session
        self.user_id = user_id

    @validates("email")
    def validate_email_unique(self, email):
        # Skip the check if the email is the same as the current user's email
        user = self.db_session.query(User).get(self.user_id)
        if user.email != email and self.db_session.query(User).filter(User.email == email).first():
            raise ValidationError("Email is already taken.")

    @validates("username")
    def validate_username_unique(self, username):
        # Skip the check if the username is the same as the current user's username
        user = self.db_session.query(User).get(self.user_id)
        if user.username != username and self.db_session.query(User).filter(User.username == username).first():
            raise ValidationError("Username is already taken.")
    
    @validates("phone_number")
    def validate_phone_number_unique(self, phone_number):
        # Validate that the phone number is unique across all drivers
        if self.db_session.query(Driver).filter_by(phone_number=phone_number).first():
            raise ValidationError("Phone number is already taken.")
    
    @validates('institution_id')
    def validate_institution_id(self, value):
        # Validate that the institution ID exists in the database
        institution = Institution.query.get(value)
        if institution is None:
            raise ValidationError("Institution with the given ID does not exist.")

    @validates_schema
    def validate_passwords_match(self, data, **kwargs):
        # Ensure that password and password confirmation match
        if data.get('password') and data.get('password') != data.get('password_confirmation'):
            raise ValidationError('Passwords do not match', 'password_confirmation')

