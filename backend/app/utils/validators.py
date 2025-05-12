from flask import current_app
import ipaddress

def validate_api_key(api_key):
    """
    Validate that the provided API key is valid
    
    Args:
        api_key (str): The API key to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    expected_key = current_app.config.get('FLASK_KEY')
    if not expected_key:
        current_app.logger.warning("No FLASK_KEY configured")
        return False
    
    return api_key == expected_key

def is_ip_allowed(ip_address):
    """
    Check if an IP address is in the whitelist
    
    Args:
        ip_address (str): The IP address to check
        
    Returns:
        bool: True if allowed, False otherwise
    """
    # If whitelist is disabled, all IPs are allowed
    whitelist = current_app.config.get('IP_WHITELIST')
    if not whitelist:
        return True
    
    # Convert string whitelist to list
    if isinstance(whitelist, str):
        whitelist = [ip.strip() for ip in whitelist.split(',')]
    
    # Check if IP is in whitelist
    if ip_address in whitelist:
        return True
    
    # Check for CIDR notation in whitelist
    try:
        client_ip = ipaddress.ip_address(ip_address)
        for allowed_range in whitelist:
            if '/' in allowed_range:  # CIDR notation
                if client_ip in ipaddress.ip_network(allowed_range, strict=False):
                    return True
    except ValueError:
        # If there's an error parsing IPs, fail closed (secure)
        current_app.logger.warning(f"Error parsing IP address: {ip_address}")
        return False
    
    return False

def clean_filename(filename):
    """
    Clean a filename to prevent path traversal and other attacks
    
    Args:
        filename (str): The filename to clean
        
    Returns:
        str: Cleaned filename
    """
    # Remove any directory components
    filename = filename.replace('/', '').replace('\\', '')
    
    # Allow only alphanumeric, dash, underscore, dot
    import re
    return re.sub(r'[^a-zA-Z0-9\-_\.]', '', filename)