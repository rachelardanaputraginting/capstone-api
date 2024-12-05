from flask_seeder import Seeder
from app.models import Vehicle

class VehicleSeeder(Seeder):

    def run(self):
        # Cek jika data kendaraan sudah ada untuk instansi 1, mencegah duplikasi
        if Vehicle.query.filter_by(institution_id=1).count() == 0:
            vehicles = [
                Vehicle(
                    institution_id=1,
                    driver_id=1,
                    name='Ambulance 1',
                    description='Ambulance untuk layanan darurat medis.',
                    is_ready=True,
                    picture='ambulance_1.jpg'
                ),
                Vehicle(
                    institution_id=1,
                    driver_id=2,
                    name='Ambulance 2',
                    description='Ambulance untuk layanan darurat medis cadangan.',
                    is_ready=True,
                    picture='ambulance_2.jpg'
                )
            ]
            
            # Menambahkan kendaraan ke database
            self.db.session.add_all(vehicles)
            self.db.session.commit()
            print("Vehicles seeded successfully!")
        else:
            print("Vehicles already exist for institution ID 1.")
