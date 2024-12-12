from marshmallow import Schema, fields, validate, ValidationError
from marshmallow.decorators import validates
from sqlalchemy.orm import Session
from app.models.models import Resident, Institution

class CreateIncidentSchema(Schema):
    description = fields.String(
        required=True, 
        error_messages={
            "required": "Deskripsi wajib diisi.",
            "null": "Deskripsi tidak boleh kosong."
        }
    )
    institution_id = fields.Integer(
        required=True,
        error_messages={
            "required": "ID institusi wajib diisi.",
            "null": "ID institusi tidak boleh kosong.",
            "invalid": "ID institusi harus berupa angka."
        }
    )
    resident_id = fields.Integer(
        required=True,
        error_messages={
            "required": "ID pengemudi wajib diisi.",
            "null": "ID pengemudi tidak boleh kosong.",
            "invalid": "ID pengemudi harus berupa angka."
        }
    )
    latitude = fields.Decimal(
        required=True,
        as_string=True,  # Menyimpan sebagai string untuk menghindari kehilangan presisi
        validate=validate.Range(min=-90, max=90, error="Longitude harus antara -90 dan 90."),  
        eerror_messages={
            "required": "Latitude wajib diisi.",
            "invalid": "Format email tidak valid."
        }
    )
    longitude = fields.Decimal(
        required=True,
        as_string=True,  # Menyimpan sebagai string untuk menghindari kehilangan presisi
        validate=validate.Range(min=-180, max=180, error="Latitude harus antara -180 dan 180."), 
        error_messages={
            "required": "Longitude wajib diisi.",
            "invalid": "Format email tidak valid."
        }
    )
    picture = fields.String(
        required=False,
        error_messages={
            "null": "Gambar tidak boleh kosong."
        }
    )

    def __init__(self, db_session: Session, *args, **kwargs):
        # Inisialisasi skema dengan sesi database."""
        super().__init__(*args, **kwargs)
        self.db_session = db_session
    
    @validates('description')
    def validate_description(self, value):
        # Validasi panjang karakter maksimal 75
        if len(value) > 75:
            raise ValidationError("Deskripsi tidak boleh lebih dari 75 karakter.")
        
        # Validasi jumlah kata maksimal 12
        word_count = len(value.split())
        if word_count > 12:
            raise ValidationError("Deskripsi tidak boleh lebih dari 12 kata.")

    @validates('institution_id')
    def validate_institution_id(self, value):
        # Validasi bahwa ID institusi ada di database.
        institution = self.db_session.query(Institution).get(value)
        if institution is None:
            raise ValidationError("Institusi dengan ID yang diberikan tidak ditemukan.")

    @validates('resident_id')
    def validate_driver_id(self, value):
        # Validasi bahwa ID masyarakat ada di database.
        resident = self.db_session.query(Resident).get(value)
        if resident is None:
            raise ValidationError("Masyarakat dengan ID yang diberikan tidak ditemukan.")