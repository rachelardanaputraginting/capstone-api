from marshmallow import Schema, fields, validate, ValidationError, EXCLUDE
from marshmallow.decorators import validates, validates_schema
from sqlalchemy.orm import Session
from app.models.models import Driver, Institution, Vehicle

class UpdateVehicleSchema(Schema):
    class Meta:
        unknown = EXCLUDE  # Ignore unknown fields

    name = fields.String(
        validate=[validate.Length(min=1, max=50)], 
        required=False,  # Tidak wajib
        allow_none=False  # Tapi jika diberikan, tidak boleh None
    )
    description = fields.String(
        required=False, 
        validate=[validate.Length(max=500)]  # Contoh batasan panjang
    )
    institution_id = fields.Integer(required=False)
    driver_id = fields.Integer(required=False)
    is_ready = fields.Boolean(required=False)
    picture = fields.String(
        validate=[validate.Length(max=255)], 
        required=False
    )

    def __init__(self, db_session: Session, vehicle_id: int, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db_session = db_session
        self.vehicle_id = vehicle_id
        # Ambil kendaraan saat ini untuk referensi
        self.current_vehicle = self.db_session.query(Vehicle).get(vehicle_id)

    @validates('institution_id')
    def validate_institution_id(self, value):
        if value is not None:  # Hanya validasi jika nilai diberikan
            institution = self.db_session.query(Institution).get(value)
            if not institution:
                raise ValidationError("Institution dengan ID tersebut tidak ditemukan")

    @validates('driver_id')
    def validate_driver_id(self, value):
        if value is not None:  # Hanya validasi jika nilai diberikan
            driver = self.db_session.query(Driver).get(value)
            if not driver:
                raise ValidationError("Driver dengan ID tersebut tidak ditemukan")