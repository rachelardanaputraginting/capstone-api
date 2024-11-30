from marshmallow import Schema, fields, validate, ValidationError, EXCLUDE
from sqlalchemy.orm import Session
from app.models.models import Role

class CreateRoleSchema(Schema):
    name = fields.String(
        required=True, 
        validate=[validate.Length(min=5, error="Nama role harus minimal 3 karakter.")],
        error_messages={
            "required": "Nama role wajib diisi.",
            "null": "Nama role tidak boleh kosong."
        }
    )

class UpdateRoleSchema(Schema):
    class Meta:
        unknown = EXCLUDE  # Abaikan field yang tidak dikenal
        
    def __init__(self, db_session: Session, role_id: int, *args, **kwargs):
        # Inisialisasi skema dengan sesi database dan ID kendaraan.
        super().__init__(*args, **kwargs)
        self.db_session = db_session
        self.role_id = role_id
        # Ambil kendaraan saat ini untuk referensi
        # Pindahkan pengecekan ke __init__
        self.current_role = self.db_session.query(Role).get(role_id)
        if not self.current_role:
            raise ValidationError({'role_id': 'Role tidak ditemukan'})
        
    name = fields.String(
        required=False, 
        validate=[validate.Length(min=5, error="Nama role harus minimal 3 karakter.")],
        error_messages={
            "null": "Nama role tidak boleh kosong."
        }
    )