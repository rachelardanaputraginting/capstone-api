from marshmallow import Schema, fields, validate, ValidationError
from marshmallow.decorators import validates
from sqlalchemy.orm import Session
from app.models.models import Driver, Institution

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
            raise ValidationError("Institution with the given ID does not exist.")

    @validates('driver_id')
    def validate_driver_id(self, value):
        """Validate that the driver ID exists in the database."""
        driver = self.db_session.query(Driver).get(value)
        if driver is None:
            raise ValidationError("Driver with the given ID does not exist.")
