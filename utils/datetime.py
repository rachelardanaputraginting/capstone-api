from datetime import datetime
import pytz

def get_current_time_in_timezone(timezone='Asia/Jakarta'):
    """
    Mengembalikan waktu saat ini sesuai dengan zona waktu yang diberikan.
    Default adalah zona waktu WIB (Asia/Jakarta).
    
    Args:
        timezone (str): Nama zona waktu. Contoh: 'Asia/Jakarta', 'Asia/Makassar', 'Asia/Jayapura'.
        
    Returns:
        datetime: Objek datetime sesuai zona waktu yang diberikan.
    """
    try:
        tz = pytz.timezone(timezone)
        return datetime.now(tz)
    except pytz.UnknownTimeZoneError:
        raise ValueError(f"Zona waktu tidak valid: {timezone}")
