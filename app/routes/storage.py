import io
import os
from flask import Blueprint, send_file, jsonify
from google.cloud import storage  # Pastikan sudah diinstall dengan pip

storage_route = Blueprint('storage', __name__)
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = 'credentials.json'

storage_route = Blueprint('storage', __name__)

@storage_route.route('/<folder>/<path:filepath>', methods=['GET'])
def view_file(folder, filepath):
    try:
        # Inisialisasi klien penyimpanan
        storage_client = storage.Client()
        bucket_name = 'instahelp'
        bucket = storage_client.bucket(bucket_name)
        
        # Membangun jalur gumpalan penuh
        full_path = f"{folder}/{filepath}"
        blob = bucket.blob(full_path)
        
        # Periksa apakah ada gumpalan
        if not blob.exists():
            return jsonify(
                status=False,
                message='File not found.'
            ), 404
        
        # Unduh konten gumpalan
        file_content = blob.download_as_bytes()
        
        # Menentukan jenis konten
        content_type = blob.content_type or 'application/octet-stream'
        
        # Kirim file
        return send_file(
            io.BytesIO(file_content), 
            mimetype=content_type, 
            as_attachment=False, 
            download_name=filepath
        )
    
    except Exception as e:
        return jsonify(
            status=False,
            message=f'Error retrieving file: {str(e)}'
        ), 500