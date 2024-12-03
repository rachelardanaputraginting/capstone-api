from flask_seeder import Seeder
from werkzeug.security import generate_password_hash
from app.models import (
    User, Role, UserRole, 
    Resident, Administration, 
    Institution, Driver
)
from utils.datetime import get_current_time_in_timezone
from datetime import date

class UserSeeder(Seeder):
    def run(self):
        # Seed users for each role
        self.seed_administration_users()
        self.seed_institution_users()
        self.seed_resident_users()
        self.seed_driver_users()

    def create_user_with_role(self, name, email, username, role_name, address='Sample Address'):
        try:
            # Hash a default password
            hashed_password = generate_password_hash('password123')
            
            # Get the role first
            role = Role.query.filter_by(name=role_name).first()
            if not role:
                print(f"Role {role_name} not found")
                return None, None
            
            # Create user
            user = User(
                name=name,
                email=email,
                username=username,
                password=hashed_password,
                address=address,
                email_verified_at=get_current_time_in_timezone('Asia/Jakarta')  # WIB
            )
            
            # Add user to session first to get ID
            self.db.session.add(user)
            self.db.session.flush()
            
            # Create user role association
            user_role = UserRole(
                user_id=user.id,
                role_id=role.id
            )
            self.db.session.add(user_role)
            
            return user, role
            
        except Exception as e:
            self.db.session.rollback()
            print(f"Error creating user: {str(e)}")
            return None, None

    def seed_administration_users(self):
        if Administration.query.count() == 0:
            admin_users = [
                {
                    'name': 'Admin User 1',
                    'email': 'admin1@example.com',
                    'username': 'admin_user1'
                },
                {
                    'name': 'Admin User 2', 
                    'email': 'admin2@example.com',
                    'username': 'admin_user2'
                }
            ]
            
            try:
                for admin_data in admin_users:
                    user, role = self.create_user_with_role(
                        admin_data['name'], 
                        admin_data['email'], 
                        admin_data['username'], 
                        'administration'
                    )
                    
                    if user and role:
                        # Create administration entry
                        administration = Administration(
                            user_id=user.id
                        )
                        self.db.session.add(administration)
                
                self.db.session.commit()
                print("Administration users seeded successfully!")
            except Exception as e:
                self.db.session.rollback()
                print(f"Error seeding administration users: {str(e)}")
        else:
            print("Administration users already exist.")

    def seed_institution_users(self):
        if Institution.query.count() == 0:
            institution_users = [
                {
                    'name': 'RSUD Cut Meutia',
                    'email': 'institution1@example.com',
                    'username': 'institution_user1',
                    'description': 'RSUD Cut Meutia Lhokseumawe adalah rumah sakit rujukan yang melayani rawat jalan dan rawat inap untuk berbagai kasus medis. Layanan gawat darurat 24 jam siap menangani kondisi kritis. Didukung poliklinik spesialis, laboratorium, radiologi, farmasi, dan kamar bersalin, rumah sakit ini berkomitmen pada kualitas pelayanan dan kenyamanan pasien',
                    'latitude': -6.200000,
                    'longitude': 106.816666
                },
                {
                    'name': 'RSUD Bidadari',
                    'email': 'institution2@example.com',
                    'username': 'institution_user2',
                    'description': 'RSUD Bidadari Lhokseumawe adalah rumah sakit rujukan yang melayani rawat jalan dan rawat inap untuk berbagai kasus medis. Layanan gawat darurat 24 jam siap menangani kondisi kritis. Didukung poliklinik spesialis, laboratorium, radiologi, farmasi, dan kamar bersalin, rumah sakit ini berkomitmen pada kualitas pelayanan dan kenyamanan pasien',
                    'latitude': -7.250445,
                    'longitude': 112.768845
                }
            ]
            
            try:
                for inst_data in institution_users:
                    user, role = self.create_user_with_role(
                        inst_data['name'], 
                        inst_data['email'], 
                        inst_data['username'], 
                        'institution'
                    )
                    
                    if user and role:
                        # Create institution entry
                        institution = Institution(
                            user_id=user.id,
                            description=inst_data['description'],
                            latitude=inst_data['latitude'],
                            longitude=inst_data['longitude']
                        )
                        self.db.session.add(institution)
                
                self.db.session.commit()
                print("Institution users seeded successfully!")
            except Exception as e:
                self.db.session.rollback()
                print(f"Error seeding institution users: {str(e)}")
        else:
            print("Institution users already exist.")

    def seed_resident_users(self):
        if Resident.query.count() == 0:
            resident_users = [
                {
                    'name': 'Resident User 1',
                    'email': 'resident1@example.com',
                    'username': 'resident_user1',
                    'nik': '1234567890123456',
                    'date_of_birth': date(1990, 1, 15),
                    'place_of_birth': 'Jakarta',
                    'gender': 'FEMALE',
                    'phone_number': '081234567890'
                },
                {
                    'name': 'Resident User 2',
                    'email': 'resident2@example.com',
                    'username': 'resident_user2',
                    'nik': '6543210987654321',
                    'date_of_birth': date(1995, 5, 20),
                    'place_of_birth': 'Surabaya',
                    'gender': 'MALE',
                    'phone_number': '087654321098'
                }
            ]
            
            try:
                for resident_data in resident_users:
                    user, role = self.create_user_with_role(
                        resident_data['name'], 
                        resident_data['email'], 
                        resident_data['username'], 
                        'resident'
                    )
                    
                    if user and role:
                        # Create resident entry
                        resident = Resident(
                            user_id=user.id,
                            nik=resident_data['nik'],
                            date_of_birth=resident_data['date_of_birth'],
                            place_of_birth=resident_data['place_of_birth'],
                            gender=resident_data['gender'],
                            phone_number=resident_data['phone_number']
                        )
                        self.db.session.add(resident)
                
                self.db.session.commit()
                print("Resident users seeded successfully!")
            except Exception as e:
                self.db.session.rollback()
                print(f"Error seeding resident users: {str(e)}")
        else:
            print("Resident users already exist.")

    def seed_driver_users(self):
        if Driver.query.count() == 0:
            # Get some existing institutions
            institutions = Institution.query.limit(2).all()
            
            if not institutions:
                print("No institutions found. Please seed institutions first.")
                return
            
            driver_users = [
                {
                    'name': 'Driver User 1',
                    'email': 'driver1@example.com',
                    'username': 'driver_user1',
                    'phone_number': '082345678901',
                    'institution': institutions[0]
                },
                {
                    'name': 'Driver User 2',
                    'email': 'driver2@example.com',
                    'username': 'driver_user2',
                    'phone_number': '083456789012',
                    'institution': institutions[1]
                }
            ]
            
            try:
                for driver_data in driver_users:
                    user, role = self.create_user_with_role(
                        driver_data['name'], 
                        driver_data['email'], 
                        driver_data['username'], 
                        'driver'
                    )
                    
                    if user and role:
                        # Create driver entry
                        driver = Driver(
                            user_id=user.id,
                            institution_id=driver_data['institution'].id,
                            phone_number=driver_data['phone_number']
                        )
                        self.db.session.add(driver)
                
                self.db.session.commit()
                print("Driver users seeded successfully!")
            except Exception as e:
                self.db.session.rollback()
                print(f"Error seeding driver users: {str(e)}")
        else:
            print("Driver users already exist.")