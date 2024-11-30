from marshmallow import Schema, fields, validate, ValidationError, EXCLUDE
from marshmallow.decorators import validates
from sqlalchemy.orm import Session
from app.models.models import User, Administration
from sqlalchemy import and_

class UpdateAdministrationSchema(Schema):
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

    def __init__(self, db_session: Session, administration_id: int, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db_session = db_session
        self.administration_id = administration_id
        
        # Pindahkan pengecekan ke __init__
        self.current_administration = self.db_session.query(Administration).get(administration_id)
        if not self.current_administration:
            raise ValidationError({'administration_id': 'Admin tidak ditemukan'})

        # Cek dan set current_user
        self.current_user = self.db_session.query(User).get(self.current_administration.user_id)
        if not self.current_user:
            raise ValidationError({'user_id': 'Pengguna terkait admin tidak ditemukan'})
    
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