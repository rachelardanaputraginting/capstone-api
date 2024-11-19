from flask import Flask
from .extensions import db, jwt, migrate
from .config import Config
from .models import User, Role  # Import model-model yang diperlukan

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    
    # Register blueprints
    from .routes.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    return app
