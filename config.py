import os
from dotenv import load_dotenv
from datetime import timedelta

# Pastikan untuk memuat file .env
load_dotenv()

class InitConfig() :
    def __init__(self, app) :
        
        # Database Configuration
        db_config = {
            'host': os.getenv('DB_HOST'),
            'name': os.getenv('DB_NAME'),
            'user': os.getenv('DB_USERNAME'),
            'pass': os.getenv('DB_PASSWORD'),
            # 'port': os.getenv('DB_PORT'),
        }
        app.config['SQLALCHEMY_DATABASE_URI'] =\
            f'mysql://{db_config["user"]}:{db_config["pass"]}@{db_config["host"]}/{db_config["name"]}'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS', False)
        
        # JWT Configuration
        app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
        app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
        app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=7)
        
        # Mail Configuration
        app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
        app.config['MAIL_PORT'] = os.getenv('MAIL_PORT')
        app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
        app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
        app.config['MAIL_USE_TLS'] = True
        app.config['MAIL_USE_SSL'] = False
