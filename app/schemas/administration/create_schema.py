from marshmallow import Schema, fields, validate, ValidationError
from marshmallow.decorators import validates_schema, validates
from sqlalchemy.orm import Session
from app.models.models import User

class CreateAdministrationSchema(Schema):
    # Bidang pengguna dasar
    name = fields.String(
        required=True,
        validate=[validate.Length(min=1, max=50, error="Nama harus antara 1 hingga 50 karakter.")],
        error_messages={"required": "Nama wajib diisi."}
    )
    email = fields.Email(
        required=True,
        validate=[validate.Length(max=50, error="Email tidak boleh lebih dari 50 karakter.")],
        error_messages={"required": "Email wajib diisi.", "invalid": "Format email tidak valid."}
    )
    username = fields.String(
        required=True,
        validate=[validate.Length(min=1, max=30, error="Username harus antara 1 hingga 30 karakter.")],
        error_messages={"required": "Username wajib diisi."}
    )
    address = fields.String(
        required=True,
        validate=[validate.Length(max=500, error="Alamat tidak boleh lebih dari 500 karakter.")],
        error_messages={"required": "Alamat wajib diisi."}
    )
    password = fields.String(
        required=True,
        validate=[validate.Length(min=8, error="Kata sandi harus minimal 8 karakter.")],
        error_messages={"required": "Kata sandi wajib diisi."}
    )
    password_confirmation = fields.String(
        required=True,
        error_messages={"required": "Konfirmasi kata sandi wajib diisi."}
    )
    
    # Bidang khusus pengemudi
    role = fields.String(
        required=True,
        validate=validate.OneOf(['administration'], error="Role hanya boleh diisi dengan 'administration'."),
        error_messages={"required": "Role wajib diisi."}
    )

    def __init__(self, db_session: Session, *args, **kwargs):
        # Inisialisasi skema dengan sesi database.
        super().__init__(*args, **kwargs)
        self.db_session = db_session

    @validates("email")
    def validate_email_unique(self, email):
        if self.db_session.query(User).filter(User.email == email).first():
            raise ValidationError("Email sudah terdaftar.")

    @validates("username")
    def validate_username_unique(self, username):
        if self.db_session.query(User).filter(User.username == username).first():
            raise ValidationError("Username sudah terdaftar.")

    @validates_schema
    def validate_passwords_match(self, data, **kwargs):
        if data.get('password') != data.get('password_confirmation'):
            raise ValidationError({'password_confirmation': 'Kata sandi dan konfirmasi kata sandi tidak cocok.'})
