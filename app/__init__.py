from flask import Flask
from config import Config
from app.routes.auth import auth
from app.extensions import db, migrate, jwt
from flask_seeder import FlaskSeeder

def create_app(config_class=Config):
    # Create Flask app instance
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # JWT
    jwt.init_app(app)
    
    # Import models to ensure they're loaded
    from app.models import models
    
    seeder = FlaskSeeder()
    seeder.init_app(app, db)
    
    app.register_blueprint(auth, url_prefix='/auth')
    
    # with app.app_context():

    # # jwt.init_app(app)

    # # mail.init_app(app)
    # # mgr.init_app(app, db)
    # # app.register_blueprint(storage_route, url_prefix='/storage')
    # # app.register_blueprint(user_route, url_prefix='/user')
    # # app.register_blueprint(major_route, url_prefix='/major')
    # # app.register_blueprint(form_route, url_prefix='/form')
    # # app.register_blueprint(home_route, url_prefix='/')
    
    return app