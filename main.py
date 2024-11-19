from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.config import Config  # Mengimpor konfigurasi dari file config.py
from app.seeds import run_seeders

# Inisialisasi aplikasi Flask
app = Flask(__name__)

# Memuat konfigurasi dari file config.py
config = app.config.from_object(Config)

# Inisialisasi SQLAlchemy
db = SQLAlchemy(app)

if __name__ == '__main__':
    app.run(debug=True)
    with app.app_context():
        # Menjalankan semua seeder
        run_seeders()
