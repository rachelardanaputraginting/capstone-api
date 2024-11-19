# backend/app/manage.py

# from app.seeds.administration_seeder import run as run_administration_seeder
# from app.seeds.resident_seeder import run as run_resident_seeder
# from app.seeds.driver_seeder import run as run_driver_seeder
from app.seeds.role_seeder import run as run_role_seeder

def seed():
    # run_administration_seeder()
    # run_resident_seeder()
    # run_driver_seeder()
    run_role_seeder()

# Jalankan seeders dengan menjalankan script ini
