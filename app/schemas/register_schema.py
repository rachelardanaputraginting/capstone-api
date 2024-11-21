from marshmallow import Schema, fields, validate, ValidationError
from marshmallow.decorators import validates_schema

class ResidentRegistrationSchema(Schema):
    name = fields.String(required=True, validate=[
        validate.Length(min=1, max=255)
    ])
    email = fields.Email(required=True, validate=[
        validate.Length(max=255)
    ])
    username = fields.String(required=True, validate=[
        validate.Length(min=1, max=255)
    ])
    address = fields.String(allow_none=True, validate=[
        validate.Length(max=500)
    ])
    password = fields.String(required=True, validate=[
        validate.Length(min=8)
    ])
    password_confirmation = fields.String(required=True)
    role = fields.String(required=True, validate=validate.OneOf(['resident', 'institution']))
    
    # Resident-specific fields
    nik = fields.String(required=True, validate=[
        validate.Length(equal=16)
    ])
    date_of_birth = fields.Date(required=True)
    place_of_birth = fields.String(required=True)
    gender = fields.String(required=True, validate=validate.OneOf(['MAN', 'WOMEN']))
    phone_number = fields.String(required=True)

    @validates_schema
    def validate_passwords_match(self, data, **kwargs):
        if data.get('password') != data.get('password_confirmation'):
            raise ValidationError('Passwords do not match', 'password_confirmation')

class InstitutionRegistrationSchema(Schema):
    name = fields.String(required=True, validate=[
        validate.Length(min=1, max=255)
    ])
    email = fields.Email(required=True, validate=[
        validate.Length(max=255)
    ])
    username = fields.String(required=True, validate=[
        validate.Length(min=1, max=255)
    ])
    address = fields.String(required=True, validate=[
        validate.Length(max=500)
    ])
    password = fields.String(required=True, validate=[
        validate.Length(min=8)
    ])
    password_confirmation = fields.String(required=True)
    role = fields.String(required=True, validate=validate.OneOf(['resident', 'institution']))
    
    # Institution-specific fields
    description = fields.String(required=True)
    latitude = fields.Float(required=True)
    longitude = fields.Float(required=True)

    @validates_schema
    def validate_passwords_match(self, data, **kwargs):
        if data.get('password') != data.get('password_confirmation'):
            raise ValidationError('Passwords do not match', 'password_confirmation')