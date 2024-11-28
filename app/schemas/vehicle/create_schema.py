from marshmallow import Schema, fields, validate, ValidationError
from marshmallow.decorators import validates, validates_schema
from sqlalchemy.orm import Session
from app.models.models import Driver, Institution, Vehicle

class CreateVehicleSchema(Schema):
    name = fields.String(required=True, validate=[validate.Length(min=1, max=50)])
    description = fields.String(required=True)
    institution_id = fields.Integer(required=True)
    driver_id = fields.Integer(required=True)
    is_ready = fields.Boolean(missing=True)  # Default True jika tidak diberikan
    picture = fields.String(
        required=False, validate=[validate.Length(max=255)]
    )

    def __init__(self, db_session: Session, *args, **kwargs):
        """Initialize schema with a database session."""
        super().__init__(*args, **kwargs)
        self.db_session = db_session

    @validates('institution_id')
    def validate_institution_id(self, value):
        """Validate that the institution ID exists in the database."""
        institution = self.db_session.query(Institution).get(value)
        if institution is None:
            raise ValidationError("Institusi dengan ID yang diberikan tidak ada.")

    @validates('driver_id')
    def validate_driver_id(self, value):
        """Validate that the driver ID exists in the database."""
        driver = self.db_session.query(Driver).get(value)
        if driver is None:
            raise ValidationError("Pengemudi dengan ID yang diberikan tidak ada.")
    
    @validates_schema
    def validate_unique_constraints(self, data, **kwargs):
        # Tambahkan validasi tambahan jika dipe rlukan
        # Misalnya, memastikan driver tidak digunakan di kendaraan lain
        if 'driver_id' in data:
            existing_vehicle = self.db_session.query(Vehicle).filter(
                Vehicle.driver_id == data['driver_id']
            ).first()
            
            if existing_vehicle:
                raise ValidationError({
                    'driver_id': 'Driver sudah terdaftar pada kendaraan lain'
                })
