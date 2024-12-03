from marshmallow import Schema, fields, validate, ValidationError
from marshmallow.decorators import validates_schema, validates
from sqlalchemy.orm import Session
from app.models.models import User, Resident, Institution, Driver

class ResidentRegistrationSchema(Schema):
    # Bidang pengguna dasar
    name = fields.String(
        required=True,
        validate=[validate.Length(min=1, max=50, error="Nama harus antara 1 hingga 50 karakter.")],
        error_messages={"required": "Nama wajib diisi."}
    )
    email = fields.Email(
        required=True,
        validate=[
            validate.Length(max=50, error="Email tidak boleh lebih dari 50 karakter.")
        ],
        error_messages={
            "required": "Email wajib diisi.",
            "invalid": "Format email tidak valid."
        }
    )
    username = fields.String(
        required=True, 
        validate=[validate.Length(min=1, max=30, error="Username harus antara 1 hingga 30 karakter.")],
        error_messages={"required": "Username wajib diisi."} 
        )
    address = fields.String(
        required=True,
        validate=[validate.Length(max=100, error="Alamat tidak boleh lebih dari 100 karakter.")],
        error_messages={"required": "Alamat wajib diisi."} 
        )
    password = fields.String(
        required=True, 
        validate=[validate.Length(min=8, error="Kata sandi harus minimal 8 karakter.")],
        error_messages={"required": "Konfirmasi kata sandi wajib diisi."}
        )
    password_confirmation = fields.String(
        required=True,
        error_messages={"required": "Konfirmasi kata sandi wajib diisi."}
    )
    role = fields.String(
        required=True,
        validate=validate.OneOf(
            ['resident'], 
            error="Role harus 'resident'."
        ),
        error_messages={
            "required": "Role wajib diisi.",
            "invalid": "Role yang dimasukkan tidak valid."
        }
    )

    # Bidang khusus pengemudi
    nik = fields.String(
        required=True, 
        validate=[validate.Length(equal=16, error="NIK harus tepat 16 digit.")],
        error_messages={"required": "NIK wajib diisi."}    
    )
    date_of_birth = fields.Date(
        required=True,
        error_messages={
            "required": "Tanggal lahir wajib diisi.",
            "invalid": "Format tanggal lahir tidak valid. Gunakan format YYYY-MM-DD."
        }
    )
    place_of_birth = fields.String(
        required=True,
        validate=[validate.Length(max=50, error="Tempat lahir tidak boleh lebih dari 50 karakter.")],
        error_messages={"required": "Tempat lahir wajib diisi."}   
    )
    gender = fields.String(
        required=True,
        validate=validate.OneOf(
            ['FEMALE', 'FEMALE'], 
            error="Jenis kelamin hanya boleh 'Pria' atau 'Wanita'."),
        error_messages={"required": "Jenis kelamin wajib diisi."}
    )
    phone_number = fields.String(
        required=True,
        validate=[
            validate.Length(min=10, max=13, error="Nomor telepon harus antara 10 hingga 13 digit."),
            validate.Regexp(r'^\d+$', error="Nomor telepon hanya boleh berisi angka.")
        ],
        error_messages={"required": "Nomor telepon wajib diisi."}
    )

    def __init__(self, db_session: Session, *args, **kwargs):
        # Inisialisasi skema dengan sesi basis data.
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

    @validates("nik")
    def validate_nik_unique(self, nik):
        if self.db_session.query(Resident).filter_by(nik=nik).first():
            raise ValidationError("NIK sudah terdaftar.")
        
    @validates("phone_number")
    def validate_nik_unique(self, phone_number):
        if self.db_session.query(Resident).filter_by(phone_number=phone_number).first():
            raise ValidationError("Nomor Telepon sudah terdaftar.")
        elif self.db_session.query(Driver).filter_by(phone_number=phone_number).first():
            raise ValidationError("Nomor Telepon sudah terdaftar.")

    @validates_schema
    def validate_passwords_match(self, data, **kwargs):
        if data.get('password') != data.get('password_confirmation'):
            raise ValidationError({'password_confirmation': 'Kata sandi dan konfirmasi kata sandi tidak cocok.'})


class InstitutionRegistrationSchema(Schema):
    # Bidang pengguna dasar
    name = fields.String(
        required=True,
        validate=[validate.Length(min=1, max=50, error="Nama harus antara 1 hingga 50 karakter.")],
        error_messages={"required": "Nama wajib diisi."}
    )  
    email = fields.Email(
         required=True,
        validate=[
            validate.Length(max=50, error="Email tidak boleh lebih dari 50 karakter.")
        ],
        error_messages={
            "required": "Email wajib diisi.",
            "invalid": "Format email tidak valid."
        }
    )
    username = fields.String(
        required=True, 
        validate=[validate.Length(min=1, max=30, error="Username harus antara 1 hingga 30 karakter.")],
        error_messages={"required": "Username wajib diisi."} 
    )
    address = fields.String(
        required=True,
        validate=[validate.Length(max=100, error="Alamat tidak boleh lebih dari 100 karakter.")],
        error_messages={"required": "Alamat wajib diisi."} 
    )
    password = fields.String(
        required=True, 
        validate=[validate.Length(min=8, error="Kata sandi harus minimal 8 karakter.")],
        error_messages={"required": "Konfirmasi kata sandi wajib diisi."}
    )
    password_confirmation = fields.String(
        required=True,
        error_messages={"required": "Konfirmasi kata sandi wajib diisi."}
    )
    role = fields.String(
        required=True,
        validate=validate.OneOf(
            ['institution'], 
            error="Role harus 'institution'."
        ),
        error_messages={
            "required": "Role wajib diisi.",
            "invalid": "Role yang dimasukkan tidak valid."
        }
    )

    # Bidang khusus Institusi
    description = fields.String(
        required=True,
        validate=[
            validate.Length(min=50, max=400, error="Deskripsi harus antara 50 hingga 200 karakter.")
        ],
        error_messages={"required": "Deskripsi wajib diisi."}
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
    def __init__(self, db_session: Session, *args, **kwargs):
        # Inisialisasi skema dengan sesi basis data.
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
