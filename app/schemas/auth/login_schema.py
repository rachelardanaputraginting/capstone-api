from marshmallow import Schema, fields, validate

class LoginSchema(Schema):
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
   password = fields.String(
        required=True,
        validate=[validate.Length(min=8, error="Kata sandi harus minimal 8 karakter.")],
        error_messages={"required": "Kata sandi wajib diisi."}
    ) 