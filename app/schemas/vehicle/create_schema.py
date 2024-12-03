from marshmallow import Schema, fields, validate, ValidationError
from marshmallow.decorators import validates, validates_schema
from sqlalchemy.orm import Session
from app.models.models import Driver, Institution, Vehicle

class CreateVehicleSchema(Schema):
    name = fields.String(
        required=True, 
        validate=[validate.Length(min=1, max=50, error="Nama kendaraan harus antara 1 hingga 50 karakter.")],
        error_messages={
            "required": "Nama kendaraan wajib diisi.",
            "null": "Nama kendaraan tidak boleh kosong."
        }
    )
    description = fields.String(
        required=True,
        validate=[validate.Length(min=50, error="Deskripsi minimal harus 50 karakter.")],
        error_messages={
            "required": "Deskripsi kendaraan wajib diisi.",
            "null": "Deskripsi kendaraan tidak boleh kosong."
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
    driver_id = fields.Integer(
        required=True,
        error_messages={
            "required": "ID pengemudi wajib diisi.",
            "null": "ID pengemudi tidak boleh kosong.",
            "invalid": "ID pengemudi harus berupa angka."
        }
    )
    is_ready = fields.Boolean(
        missing=True,  # Default True jika tidak diberikan
        error_messages={
            "invalid": "Status kesiapan kendaraan harus berupa nilai boolean."
        }
    )
    picture = fields.String(
        required=False, 
        validate=[validate.Length(max=255, error="Panjang gambar tidak boleh melebihi 255 karakter.")],
        error_messages={
            "null": "Gambar tidak boleh kosong."
        }
    )

    def __init__(self, db_session: Session, *args, **kwargs):
        # Inisialisasi skema dengan sesi database."""
        super().__init__(*args, **kwargs)
        self.db_session = db_session

    @validates('institution_id')
    def validate_institution_id(self, value):
        # Validasi bahwa ID institusi ada di database.
        institution = self.db_session.query(Institution).get(value)
        if institution is None:
            raise ValidationError("Institusi dengan ID yang diberikan tidak ditemukan.")

    @validates('driver_id')
    def validate_driver_id(self, value):
        # Validasi bahwa ID pengemudi ada di database.
        driver = self.db_session.query(Driver).get(value)
        if driver is None:
            raise ValidationError("Pengemudi dengan ID yang diberikan tidak ditemukan.")
    
    @validates_schema
    def validate_unique_constraints(self, data, **kwargs):
        # Validasi tambahan untuk memastikan driver belum terdaftar di kendaraan lain.
        if 'driver_id' in data:
            existing_vehicle = self.db_session.query(Vehicle).filter(
                Vehicle.driver_id == data['driver_id']
            ).first()
            
            if existing_vehicle:
                raise ValidationError({
                    'driver_id': 'Pengemudi sudah terdaftar pada kendaraan lain'
                })