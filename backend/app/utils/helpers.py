import hashlib
import os
import random
import string
from datetime import datetime, timezone, timedelta
from flask import current_app

def hash_ip(ip_address):
    """
    Create a hash of an IP address for identification without storing the actual IP
    
    Args:
        ip_address (str): The IP address to hash
        
    Returns:
        str: Hashed IP address
    """
    return hashlib.md5(ip_address.encode()).hexdigest()[:10]

def generate_random_string(length=20):
    """
    Generate a random string of lowercase letters
    
    Args:
        length (int): Length of the random string
        
    Returns:
        str: Random string
    """
    return ''.join(random.choice(string.ascii_lowercase) for _ in range(length))

def generate_filename(ip_hash, file_type):
    """
    Generate a unique filename for exports
    
    Args:
        ip_hash (str): Hash of the user's IP address
        file_type (str): File extension ('csv', 'html', etc.)
        
    Returns:
        str: Generated filename
    """
    timestamp = datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')
    random_str = generate_random_string(10)
    return f"{ip_hash}_{timestamp}_{random_str}.{file_type}"

def ensure_directory_exists(directory):
    """
    Ensure a directory exists, creating it if necessary
    
    Args:
        directory (str): Directory path
        
    Returns:
        bool: True if directory exists or was created, False on error
    """
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
        return True
    except Exception as e:
        current_app.logger.error(f"Error creating directory {directory}: {str(e)}")
        return False

def format_datetime(dt, format_str='%Y-%m-%d %H:%M:%S UTC'):
    """
    Format a datetime object to string
    
    Args:
        dt (datetime): Datetime object
        format_str (str): Format string
        
    Returns:
        str: Formatted datetime string
    """
    if not dt:
        return None
    return dt.strftime(format_str)

def format_ip_for_display(ip, obfuscate=False):
    """
    Format an IP address for display, optionally obfuscating it
    
    Args:
        ip (str): IP address
        obfuscate (bool): Whether to obfuscate the IP
        
    Returns:
        str: Formatted IP address
    """
    if obfuscate:
        return ip.replace('.', '(.)').replace(':', '(:)')
    return ip