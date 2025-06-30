import hashlib
import re
from flask import request

def generate_device_fingerprint(request):
    """Générer une empreinte unique de l'appareil"""
    # Collecter les informations de l'appareil
    user_agent = request.headers.get('User-Agent', '')
    accept_language = request.headers.get('Accept-Language', '')
    accept_encoding = request.headers.get('Accept-Encoding', '')
    ip_address = request.remote_addr or request.headers.get('X-Forwarded-For', '127.0.0.1')
    
    # Combiner les informations
    device_string = f"{user_agent}|{accept_language}|{accept_encoding}|{ip_address}"
    
    # Générer un hash SHA-256
    device_hash = hashlib.sha256(device_string.encode('utf-8')).hexdigest()
    
    return device_hash

def get_device_name(request):
    """Extraire le nom de l'appareil depuis le User-Agent"""
    user_agent = request.headers.get('User-Agent', '')
    
    # Patterns pour détecter différents types d'appareils
    patterns = {
        'iPhone': r'iPhone',
        'iPad': r'iPad',
        'Android': r'Android',
        'Windows': r'Windows NT',
        'Mac': r'Mac OS X',
        'Linux': r'Linux',
        'Chrome': r'Chrome',
        'Firefox': r'Firefox',
        'Safari': r'Safari',
        'Edge': r'Edge'
    }
    
    detected_devices = []
    
    for device_name, pattern in patterns.items():
        if re.search(pattern, user_agent, re.IGNORECASE):
            detected_devices.append(device_name)
    
    if detected_devices:
        return ' '.join(detected_devices[:2])  # Limiter à 2 détections
    else:
        return 'Unknown Device'

def get_browser_info(request):
    """Extraire les informations du navigateur"""
    user_agent = request.headers.get('User-Agent', '')
    
    browser_patterns = {
        'Chrome': r'Chrome/(\d+\.\d+)',
        'Firefox': r'Firefox/(\d+\.\d+)',
        'Safari': r'Version/(\d+\.\d+)',
        'Edge': r'Edge/(\d+\.\d+)'
    }
    
    for browser, pattern in browser_patterns.items():
        match = re.search(pattern, user_agent)
        if match:
            return {
                'name': browser,
                'version': match.group(1)
            }
    
    return {
        'name': 'Unknown',
        'version': 'Unknown'
    }

def get_os_info(request):
    """Extraire les informations du système d'exploitation"""
    user_agent = request.headers.get('User-Agent', '')
    
    os_patterns = {
        'Windows': r'Windows NT (\d+\.\d+)',
        'Mac': r'Mac OS X (\d+[._]\d+)',
        'Linux': r'Linux',
        'Android': r'Android (\d+\.\d+)',
        'iOS': r'iPhone OS (\d+[._]\d+)'
    }
    
    for os_name, pattern in os_patterns.items():
        match = re.search(pattern, user_agent)
        if match:
            version = match.group(1) if len(match.groups()) > 0 else 'Unknown'
            return {
                'name': os_name,
                'version': version
            }
    
    return {
        'name': 'Unknown',
        'version': 'Unknown'
    } 