import os
import time
import random
import string
from flask import current_app
from google.cloud import storage

def upload_file_to_gcs(file, directory='incidents'):
    # Mengunggah file ke Google Cloud Storage
    # :file param: Objek file dari permintaan
    # :param direktori: Direktori dalam bucket yang akan diunggah (default: insiden)
    # :return: Kamus dengan status unggahan dan URL file
    
    try:
        # Inisialisasi klien penyimpanan
        storage_client = storage.Client()
        bucket_name = os.getenv('BUCKET_NAME', 'instahelp')
        bucket = storage_client.bucket(bucket_name)
        
        # Menghasilkan nama file yang unik
        timestamp = int(time.time())
        random_string = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        ext = file.filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{timestamp}_{random_string}.{ext}"
        
        # Membangun jalur gumpalan dengan direktori
        blob_path = f"{directory}/{unique_filename}"
        blob = bucket.blob(blob_path)
        
        # Mengatur jenis konten berdasarkan ekstensi file
        content_types = {
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
        }
        content_type = content_types.get(ext, 'application/octet-stream')
        blob.content_type = content_type
        
        # Atur ulang penunjuk file dan unggah
        file.seek(0)
        blob.upload_from_file(file)
        
        # Membuat gumpalan dapat diakses oleh publik
        blob.make_public()
        
        return {
            'status': True,
            'url': blob.public_url,
            'filename': unique_filename
        }
    
    except Exception as e:
        current_app.logger.error(f"Upload error: {str(e)}")
        return {
            'status': False,
            'message': str(e)
        }

def allowed_file(filename):
    # Periksa apakah ekstensi file diperbolehkan
    
    # :param nama file: Nama file
    # :return: Boolean yang menunjukkan apakah file diperbolehkan
    ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS