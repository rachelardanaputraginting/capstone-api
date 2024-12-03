from flask import Flask

# router
from app.routes.auth import auth_bp
from app.routes.administration import admin_route
from app.routes.role import role_route
from app.routes.profile import user_route
from app.routes.institution.driver import driver_route
from app.routes.institution.vehicle import vehicle_route
from app.routes.institution.institution import institution_route
from app.routes.incident.incident_resident import incident_resident_route
from app.routes.incident.incident_institution import incident_institution_route

from app.extensions import db, migrate, jwt, mail
from flask_seeder import FlaskSeeder
from dotenv import load_dotenv
from config import InitConfig
from app.models import models
from utils.error_handlers import register_error_handlers

# Create Flask app instance
app = Flask(__name__)
# app.static_folder = 'static'

seeder = FlaskSeeder()

load_dotenv('.env')

with app.app_context():
    InitConfig(app)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    mail.init_app(app)
    seeder.init_app(app, db)
    
    # Register error handlers
    register_error_handlers(app)
        
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_route, url_prefix='/administrations')
    app.register_blueprint(role_route, url_prefix='/roles')
    app.register_blueprint(user_route, url_prefix='/profiles')
    app.register_blueprint(institution_route, url_prefix='/institutions')
    app.register_blueprint(driver_route, url_prefix='/institutions/drivers')
    app.register_blueprint(vehicle_route, url_prefix='/institutions/vehicles')
    app.register_blueprint(incident_resident_route, url_prefix='/incidents/residents')
    app.register_blueprint(incident_institution_route, url_prefix='/incidents/institutions')
    
    # with app.app_context():

    # # jwt.init_app(app)

    # # mail.init_app(app)
    # # mgr.init_app(app, db)
    # # app.register_blueprint(storage_route, url_prefix='/storage')
    # # app.register_blueprint(user_route, url_prefix='/user')
    # # app.register_blueprint(major_route, url_prefix='/major')
    # # app.register_blueprint(form_route, url_prefix='/form')
    # # app.register_blueprint(home_route, url_prefix='/')
    