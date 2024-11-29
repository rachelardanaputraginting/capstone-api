from marshmallow import Schema, fields, validate, ValidationError, EXCLUDE
from marshmallow.decorators import validates
from sqlalchemy.orm import Session
from app.models.models import User, Driver, Institution, Resident
from sqlalchemy import and_

class UpdateDriverSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    # Bidang pengguna dasar
    name = fields.String(
        validate=[validate.Length(min=1, max=255, error="Nama harus antara 1 hingga 255 karakter.")], 
        required=False, 
        allow_none=False,
        error_messages={"null": "Nama tidak boleh kosong."}
    )
    email = fields.Email(
        validate=[validate.Length(max=255, error="Email tidak boleh lebih dari 255 karakter.")], 
        required=False, 
        allow_none=False,
        error_messages={
            "null": "Email tidak boleh kosong.",
            "invalid": "Format email tidak valid."
        }
    )
    username = fields.String(
        validate=[validate.Length(min=1, max=255, error="Username harus antara 1 hingga 255 karakter.")], 
        required=False, 
        allow_none=False,
        error_messages={"null": "Username tidak boleh kosong."}
    )
    address = fields.String(
        validate=[validate.Length(min=1, max=500, error="Alamat harus antara 1 hingga 500 karakter.")], 
        required=False, 
        allow_none=False,
        error_messages={"null": "Alamat tidak boleh kosong."}
    )
    
    # Bidang khusus pengemudi
    phone_number = fields.String(
        validate=[
            validate.Length(min=10, max=13, error="Nomor telepon harus antara 10 hingga 13 digit."),
            validate.Regexp(r'^\d+$', error='Nomor telepon hanya boleh berisi angka.')
        ], 
        required=False, 
        allow_none=False,
        error_messages={"null": "Nomor telepon tidak boleh kosong."}
    )
    institution_id = fields.Integer(
        required=False, 
        allow_none=False,
        error_messages={"null": "ID institusi tidak boleh kosong."}
    )

    def __init__(self, db_session: Session, driver_id: int, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db_session = db_session
        self.driver_id = driver_id
        
        # Pindahkan pengecekan ke __init__
        self.current_driver = self.db_session.query(Driver).get(driver_id)
        if not self.current_driver:
            raise ValidationError({'driver_id': 'Pengemudi tidak ditemukan'})

        # Cek dan set current_user
        self.current_user = self.db_session.query(User).get(self.current_driver.user_id)
        if not self.current_user:
            raise ValidationError({'user_id': 'Pengguna terkait pengemudi tidak ditemukan'})
    
    @validates("email")
    def validate_email_unique(self, email):
        if not email:  # Lewati validasi jika email tidak diberikan
            return
            
        # Periksa apakah ada email untuk pengguna lain
        existing_user = self.db_session.query(User).filter(
            and_(
                User.email == email,
                User.id != self.current_user.id
            )
        ).first()
        
        if existing_user:
            raise ValidationError("Email sudah digunakan")

    @validates("username")
    def validate_username_unique(self, username):
        if not username:  # Lewati validasi jika username tidak diberikan
            return
            
        # Periksa apakah username ada untuk pengguna lain
        existing_user = self.db_session.query(User).filter(
            and_(
                User.username == username,
                User.id != self.current_user.id
            )
        ).first()
        
        if existing_user:
            raise ValidationError("Username sudah digunakan")
    
    @validates("phone_number")
    def validate_phone_number_unique(self, phone_number):
        if not phone_number:  # Lewati validasi jika phone_number tidak tersedia
            return
            
        # Periksa apakah phone_number ada dalam tabel driver (tidak termasuk driver saat ini)
        existing_driver = self.db_session.query(Driver).filter(
            and_(
                Driver.phone_number == phone_number,
                Driver.id != self.current_driver.id
            )
        ).first()
        
        if existing_driver:
            raise ValidationError("Nomor telepon sudah digunakan")

        # Periksa apakah phone_number ada di tabel penduduk
        existing_resident = self.db_session.query(Resident).filter(
            Resident.phone_number == phone_number
        ).first()
        
        if existing_resident:
            raise ValidationError("Nomor telepon sudah digunakan")
    
    @validates('institution_id')
    def validate_institution_id(self, value):
        if not value:  # Lewati validasi jika institution_id tidak tersedia
            return
            
        institution = self.db_session.query(Institution).get(value)
        if not institution:
            raise ValidationError("Institusi dengan ID yang diberikan tidak ditemukan")