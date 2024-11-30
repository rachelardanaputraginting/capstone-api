from marshmallow import Schema, fields, validate, ValidationError, EXCLUDE
from marshmallow.decorators import validates, validates_schema
from sqlalchemy.orm import Session
from app.models.models import Institution, Vehicle

class UpdateVehicleSchema(Schema):
    class Meta:
        unknown = EXCLUDE  # Abaikan field yang tidak dikenal

    name = fields.String(
        validate=[validate.Length(min=1, max=50, error="Nama kendaraan harus antara 1 hingga 50 karakter.")], 
        required=False,  # Tidak wajib
        allow_none=False,  # Tapi jika diberikan, tidak boleh None
        error_messages={
            "null": "Nama kendaraan tidak boleh kosong.",
            "invalid": "Format nama kendaraan tidak valid."
        }
    )
    description = fields.String(
        required=False, 
        validate=[validate.Length(max=500, error="Deskripsi tidak boleh lebih dari 500 karakter.")],
        error_messages={
            "null": "Deskripsi tidak boleh kosong.",
            "invalid": "Format deskripsi tidak valid."
        }
    )
    institution_id = fields.Integer(
        required=False,
        error_messages={
            "null": "ID institusi tidak boleh kosong.",
            "invalid": "ID institusi harus berupa angka."
        }
    )
    driver_id = fields.Integer(
        required=False,
        error_messages={
            "null": "ID pengemudi tidak boleh kosong.",
            "invalid": "ID pengemudi harus berupa angka."
        }
    )
    is_ready = fields.Boolean(
        required=False,
        error_messages={
            "null": "Status kesiapan kendaraan tidak boleh kosong.",
            "invalid": "Status kesiapan kendaraan harus berupa nilai benar/salah."
        }
    )
    picture = fields.String(
        validate=[validate.Length(max=255, error="Panjang nama gambar tidak boleh melebihi 255 karakter.")], 
        required=False,
        error_messages={
            "null": "Gambar tidak boleh kosong.",
            "invalid": "Format gambar tidak valid."
        }
    )

    def __init__(self, db_session: Session, vehicle_id: int, *args, **kwargs):
        # Inisialisasi skema dengan sesi database dan ID kendaraan.
        super().__init__(*args, **kwargs)
        self.db_session = db_session
        self.vehicle_id = vehicle_id
        # Ambil kendaraan saat ini untuk referensi
        # Pindahkan pengecekan ke __init__
        self.current_vehicle = self.db_session.query(Vehicle).get(vehicle_id)
        if not self.current_vehicle:
            raise ValidationError({'vehicle_id': 'Kendaraan tidak ditemukan'})

    @validates('institution_id')
    def validate_institution_id(self, value):
        """Validasi ID institusi jika diberikan."""
        if value is not None:  # Hanya validasi jika nilai diberikan
            institution = self.db_session.query(Institution).get(value)
            if not institution:
                raise ValidationError("Institusi dengan ID yang diberikan tidak ditemukan.")

    @validates('driver_id')
    def validate_driver_id(self, value):
        # Validasi ID pengemudi jika diberikan.
        if value is not None:  # Hanya validasi jika nilai diberikan
            existing_driver = self.db_session.query(Vehicle).get(value)
            if not existing_driver:
                raise ValidationError("Pengemudi dengan ID yang diberikan tidak ditemukan.")
    
    @validates_schema
    def validate_unique_constraints(self, data, **kwargs):
        """Validasi batasan unik untuk kendaraan."""
        # Pastikan driver tidak digunakan di kendaraan lain
        if 'driver_id' in data:
            existing_vehicle = self.db_session.query(Vehicle).filter(
                Vehicle.driver_id == data['driver_id'],
                Vehicle.id != self.vehicle_id
            ).first()
            
            if existing_vehicle:
                raise ValidationError({
                    'driver_id': 'Pengemudi sudah terdaftar pada kendaraan lain'
                })