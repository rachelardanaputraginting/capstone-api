from flask_seeder import FlaskSeeder

def run_seeders():
    seeder = FlaskSeeder()
    seeder.run()
