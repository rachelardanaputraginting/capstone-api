from marshmallow import Schema, fields, validate, ValidationError
from marshmallow.decorators import validates_schema, validates

class ResetPasswordSchema(Schema):
   password = fields.String(
        required=True,
        validate=[validate.Length(min=8, error="Kata sandi harus minimal 8 karakter.")],
        error_messages={"required": "Kata sandi wajib diisi."}
   )
   password_confirmation = fields.String(
      required=True,
      error_messages={"required": "Konfirmasi kata sandi wajib diisi."}
   )
   
   @validates_schema
   def validate_passwords_match(self, data, **kwargs):
      if data.get('password') != data.get('password_confirmation'):
         raise ValidationError('Passwords do not match', 'password_confirmation')