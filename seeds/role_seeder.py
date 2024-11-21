from flask_seeder import Seeder
from app.models import Role
class RoleSeeder(Seeder):

    def run(self):
        # Cek jika data sudah ada, untuk mencegah duplikasi
        if Role.query.count() == 0:
            roles = [
                Role(name='administration'),
                Role(name='institution'),
                Role(name='resident'),
                Role(name='driver')
            ]
            
            # Menambahkan role ke database
            self.db.session.add_all(roles)
            self.db.session.commit()
            print("Roles seeded successfully!")
        else:
            print("Roles already exist in the database.")
