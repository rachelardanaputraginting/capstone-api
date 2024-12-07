import os

def StorageURL(filename):
    """
    Generate the full URL for a file stored in Google Cloud Storage.
    :param filename: Path in the bucket, e.g., 'vehicles/image.png'.
    :return: Full URL to access the file in GCS.
    """
    bucket_name = os.getenv('BUCKET_NAME')  # Nama bucket GCS
    return f"https://storage.googleapis.com/{bucket_name}/{filename}"
