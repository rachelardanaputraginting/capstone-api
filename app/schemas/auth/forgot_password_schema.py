from marshmallow import Schema, fields, validate

class ForgotPasswordSchema(Schema):
   email = fields.Email(required=True, validate=[validate.Length(max=50)])