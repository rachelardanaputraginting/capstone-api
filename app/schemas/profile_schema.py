from marshmallow import Schema, fields, validate, ValidationError
from marshmallow.decorators import validates
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models.models import User, Resident, Driver, Institution

# Skema Dasar untuk Field Pengguna Umum
class BaseProfileSchema(Schema):
    name = fields.String(
        required=False, 
        validate=[validate.Length(min=1, max=50, error="Nama harus antara 1 hingga 50 karakter.")],
        error_messages={
            "null": "Nama tidak boleh kosong.",
            "invalid": "Format nama tidak valid."
        }
    )
    email = fields.Email(
        required=False, 
        validate=[validate.Length(max=50, error="Email tidak boleh lebih dari 50 karakter.")],
        error_messages={
            "null": "Email tidak boleh kosong.",
            "invalid": "Format email tidak valid."
        }
    )
    username = fields.String(
        required=False, 
        validate=[validate.Length(min=1, max=30, error="Username harus antara 1 hingga 30 karakter.")],
        error_messages={
            "null": "Username tidak boleh kosong.",
            "invalid": "Format username tidak valid."
        }
    )
    address = fields.String(
        required=False,
        validate=[validate.Length(max=100, error="Alamat tidak boleh lebih dari 100 karakter.")],
        error_messages={
            "null": "Alamat tidak boleh kosong.",
            "invalid": "Format alamat tidak valid."
        }
    )

    def __init__(self, db_session: Session, user_id: int, *args, **kwargs):
        # Inisialisasi skema dengan sesi database dan ID pengguna.
        super().__init__(*args, **kwargs)
        self.db_session = db_session
        self.user_id = user_id
        
        # Cek dan set current_user
        self.current_user = self.db_session.query(User).get(user_id)
        if not self.current_user:
            raise ValidationError({'user_id': 'Pengguna tidak ditemukan'})

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

class ResidentProfileSchema(BaseProfileSchema):
    nik = fields.String(
        required=False, 
        validate=[validate.Length(equal=16, error="NIK harus tepat 16 digit.")],
        error_messages={
            "null": "NIK tidak boleh kosong.",
            "invalid": "Format NIK tidak valid."
        }
    )
    date_of_birth = fields.Date(
        required=False,
        error_messages={
            "null": "Tanggal lahir tidak boleh kosong.",
            "invalid": "Format tanggal lahir tidak valid. Gunakan format YYYY-MM-DD."
        }
    )
    place_of_birth = fields.String(
        required=False, 
        validate=[validate.Length(max=50, error="Tempat lahir tidak boleh lebih dari 50 karakter.")],
        error_messages={
            "null": "Tempat lahir tidak boleh kosong.",
            "invalid": "Format tempat lahir tidak valid."
        }
    )
    gender = fields.String(
        required=False, 
        validate=validate.OneOf(['MAN', 'WOMEN'], error="Jenis kelamin hanya boleh 'MAN' atau 'WOMEN'."),
        error_messages={
            "null": "Jenis kelamin tidak boleh kosong.",
            "invalid": "Pilihan jenis kelamin tidak valid."
        }
    )
    phone_number = fields.String(
        required=False,
        validate=[
            validate.Length(min=10, max=13, error="Nomor telepon harus antara 10 hingga 13 digit."),
            validate.Regexp(r'^\d+$', error="Nomor telepon hanya boleh berisi angka.")
        ],
        error_messages={"null": "Nomor telepon wajib diisi."}
    )

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

    @validates("nik")
    def validate_nik_unique(self, nik):
        if not nik:  # Lewati validasi jika phone_number tidak tersedia
            return
            
        existing = self.db_session.query(Resident).filter(
            and_(Resident.nik == nik, 
                 Resident.user_id != self.user_id)
        ).first()
        
        if existing:
            raise ValidationError("NIK sudah digunakan")

class DriverProfileSchema(BaseProfileSchema):
    phone_number = fields.String(
        required=False, 
        validate=[validate.Length(max=13, error="Nomor telepon tidak boleh lebih dari 13 digit.")],
        error_messages={
            "null": "Nomor telepon tidak boleh kosong.",
            "invalid": "Format nomor telepon tidak valid."
        }
    )
    institution_id = fields.Integer(
        required=False,
        error_messages={
            "null": "ID institusi tidak boleh kosong.",
            "invalid": "ID institusi harus berupa angka."
        }
    )

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

    @validates("institution_id")
    def validate_institution(self, institution_id):
        # # Validasi keberadaan institusi.
        institution = self.db_session.query(Institution).get(institution_id)
        if not institution:
            raise ValidationError("Institusi tidak ditemukan")

class InstitutionProfileSchema(BaseProfileSchema):
    description = fields.String(
        required=False,
        validate=[
            validate.Length(min=50, max=200, error="Deskripsi harus antara 50 hingga 200 karakter.")
        ],
        error_messages={
            "null": "Deskripsi tidak boleh kosong.",
            "invalid": "Format deskripsi tidak valid."
        }
    )
    latitude = fields.Float(
        required=False,
        as_string=True,  # Menyimpan sebagai string untuk menghindari kehilangan presisi
        validate=validate.Range(min=-90, max=90, error="Longitude harus antara -90 dan 90."),  
        error_messages={
            "null": "Latitude tidak boleh kosong.",
            "invalid": "Format latitude tidak valid."
        }
    )
    longitude = fields.Float(
        required=False,
        as_string=True,  # Menyimpan sebagai string untuk menghindari kehilangan presisi
        validate=validate.Range(min=-180, max=180, error="Latitude harus antara -180 dan 180."), 
        error_messages={
            "null": "Longitude tidak boleh kosong.",
            "invalid": "Format longitude tidak valid."
        }
    )

class AdministrationProfileSchema(BaseProfileSchema):
    pass