from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_seeder import FlaskSeeder
from flask_mail import Mail

# Create extension instances without binding to an app initially
db = SQLAlchemy()
jwt = JWTManager()
migrate = Migrate()
seeder = FlaskSeeder()
mail = Mail()