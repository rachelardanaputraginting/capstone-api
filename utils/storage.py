import os
import base64
import string
import random
import time
import magic

from google.cloud import storage
from google.oauth2 import service_account

class Storage:
    def __init__(self):
        # Pastikan path kredensial benar
        status = os.environ.get("Environment")

        if status == "production":
            GOOGLE_APPLICATION_CREDENTIALS = service_account.Credentials.from_service_account_file(
                "/SECRETS/SERVICE_ACCOUNT")
        else:
            GOOGLE_APPLICATION_CREDENTIALS = service_account.Credentials.from_service_account_file(
                os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"))
        
        self.client = storage.Client(credentials=GOOGLE_APPLICATION_CREDENTIALS)
        self.bucket = self.client.bucket(os.getenv('BUCKET_NAME'))

    def getFile(self, filepath):
        return self.bucket.blob(filepath)

    def deleteFile(self, filepath):
        try:
            blob = self.bucket.blob(filepath)
            blob.delete()
            return True
        except Exception as e:
            print(f"Error deleting file: {e}")
            return False

    def fileExists(self, filepath):
        return self.bucket.blob(filepath).exists()

    def uploadFile(self, file_base64, dir=''):
        try:
            # Pisahkan prefix jika ada
            if file_base64.startswith('data:image'):
                file_base64 = file_base64.split(',')[1]
            
            # Konversi data base64 menjadi bytes
            file_bytes = base64.b64decode(file_base64)
            
            # Dapatkan ekstensi file
            ext = self._get_file_extension(file_bytes)
            filename = self._generateFilename() + '.' + ext
            
            # Simpan file ke cloud
            full_path = f'{dir}/{filename}'
            blob = self.bucket.blob(full_path)
            
            # Upload dengan tipe konten yang sesuai
            content_type = f'image/{ext}'
            blob.upload_from_string(file_bytes, content_type=content_type)
            
            # Set file menjadi publik setelah diupload
            blob.make_public()
            
            return full_path  # Kembalikan path file untuk disimpan di database

        except Exception as e:
            print(f"Upload error: {e}")
            return None

    def _get_file_extension(self, file_data):
        file_signature = magic.from_buffer(file_data, mime=True)
        return file_signature.split('/')[1]
    
    def _generateFilename(self):
        timestamp = str(int(time.time()))
        random_chars = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        return timestamp + '_' + random_chars

# Buat instance global
storage_manager = Storage()