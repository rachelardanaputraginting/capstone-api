from app.extensions import db
from datetime import datetime
from enum import Enum
from sqlalchemy.types import BigInteger

class Gender(str, Enum):
    MAN = "man"
    WOMEN = "women"

class IncidentStatus(str, Enum):
    ON_ROUTE = "on-route"
    ARRIVED = "arrived"
    COMPLETED = "completed"

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    name = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.now())
    updated_at = db.Column(db.TIMESTAMP, onupdate=db.func.now())

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    email_verified_at = db.Column(db.TIMESTAMP)
    avatar = db.Column(db.String(255))
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.now())
    updated_at = db.Column(db.TIMESTAMP, onupdate=db.func.now())
    deleted_at = db.Column(db.TIMESTAMP)

    # Relationships (one-to-one)
    driver = db.relationship('Driver', back_populates='user', uselist=False)
    resident = db.relationship('Resident', back_populates='user', uselist=False)
    institution = db.relationship('Institution', back_populates='user', uselist=False)
    administration = db.relationship('Administration', back_populates='user', uselist=False)

    roles = db.relationship('Role', secondary='user_roles', backref='users')

    def as_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "address": self.address,
            "email": self.email,
            "username": self.username,
            "avatar": self.avatar,
            "email_verified_at": self.email_verified_at,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

class UserRole(db.Model):
    __tablename__ = 'user_roles'
    user_id = db.Column(db.BigInteger, db.ForeignKey('users.id'), primary_key=True)
    role_id = db.Column(db.BigInteger, db.ForeignKey('roles.id'), primary_key=True)

class Resident(db.Model):
    __tablename__ = 'residents'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    nik = db.Column(db.String(16), unique=True, nullable=False)
    user_id = db.Column(db.BigInteger, db.ForeignKey('users.id'), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    place_of_birth = db.Column(db.String(50), nullable=False)
    gender = db.Column(db.Enum(Gender), nullable=False)
    ktp_verified_at = db.Column(db.TIMESTAMP)
    phone_number = db.Column(db.String(13), unique=True, nullable=False)
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.now())
    updated_at = db.Column(db.TIMESTAMP, onupdate=db.func.now())

    # Relationship
    user = db.relationship('User', back_populates='resident', uselist=False)

class Administration(db.Model):
    __tablename__ = 'administrations'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.now())
    updated_at = db.Column(db.TIMESTAMP, onupdate=db.func.now())

    # Relationship
    user = db.relationship('User', back_populates='administration', uselist=False)

class Institution(db.Model):
    __tablename__ = 'institutions'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey('users.id'), nullable=False)
    description = db.Column(db.Text, nullable=False)
    latitude = db.Column(db.DECIMAL(9, 6)) 
    longitude = db.Column(db.DECIMAL(9, 6)) 
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.now())
    updated_at = db.Column(db.TIMESTAMP, onupdate=db.func.now())

    # Relationship
    user = db.relationship('User', back_populates='institution', uselist=False)
    vehicles = db.relationship('Vehicle', back_populates='institution', lazy=True)

class Driver(db.Model):
    __tablename__ = 'drivers'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    institution_id = db.Column(db.BigInteger, db.ForeignKey('institutions.id'), nullable=False)
    phone_number = db.Column(db.String(13), unique=True, nullable=False)
    user_id = db.Column(db.BigInteger, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.now())
    updated_at = db.Column(db.TIMESTAMP, onupdate=db.func.now())

    # Relationships
    vehicles = db.relationship('Vehicle', back_populates='driver')
    user = db.relationship('User', back_populates='driver', uselist=False)
    institution = db.relationship('Institution', backref='drivers')

class Vehicle(db.Model):
    __tablename__ = 'vehicles'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    institution_id = db.Column(db.BigInteger, db.ForeignKey('institutions.id'), nullable=False, index=True)
    driver_id = db.Column(db.BigInteger, db.ForeignKey('drivers.id'), nullable=False, index=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    is_ready = db.Column(db.Boolean, nullable=False, default=True)
    picture = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.now(), nullable=False)
    updated_at = db.Column(db.TIMESTAMP, onupdate=db.func.now(), nullable=True, server_default=db.func.now())

    deleted_at = db.Column(db.TIMESTAMP, nullable=True)

    # Optional: Define relationships for easier query building
    institution = db.relationship('Institution', back_populates='vehicles')
    driver = db.relationship('Driver', back_populates='vehicles')

class Incident(db.Model):
    __tablename__ = 'incidents'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    resident_id = db.Column(db.BigInteger, db.ForeignKey('residents.id'), nullable=False)
    institution_id = db.Column(db.BigInteger, db.ForeignKey('institutions.id'), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.Boolean, default=False)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    completed_at = db.Column(db.TIMESTAMP)
    reported_at = db.Column(db.TIMESTAMP)
    handle_at = db.Column(db.TIMESTAMP)
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.now())
    updated_at = db.Column(db.TIMESTAMP, onupdate=db.func.now())
    deleted_at = db.Column(db.TIMESTAMP)

    # Relationships
    resident = db.relationship('Resident', backref='incidents')
    institution = db.relationship('Institution', backref='incidents')

class IncidentVehicleOfficer(db.Model):
    __tablename__ = 'incident_vehicle_officers'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    incident_id = db.Column(db.BigInteger, db.ForeignKey('incidents.id'), nullable=False)
    vehicle_id = db.Column(db.BigInteger, db.ForeignKey('vehicles.id'), nullable=False)
    driver_id = db.Column(db.BigInteger, db.ForeignKey('drivers.id'), nullable=False)
    status = db.Column(db.Enum(IncidentStatus), nullable=False)
    assigned_at = db.Column(db.TIMESTAMP)
    completed_at = db.Column(db.TIMESTAMP)

    # Relationships
    incident = db.relationship('Incident', backref='incident_vehicle_officers')
    vehicle = db.relationship('Vehicle', backref='incident_vehicle_officers')
    driver = db.relationship('Driver', backref='incident_vehicle_officers')