from marshmallow import Schema, fields, validate

class ForgotPasswordSchema(Schema):
   email = fields.Email(
        required=True,
        validate=[
            validate.Length(max=50, error="Email tidak boleh lebih dari 50 karakter.")
        ],
        error_messages={
            "required": "Email wajib diisi.",
            "invalid": "Format email tidak valid."
        }
   )