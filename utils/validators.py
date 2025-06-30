import re
from email_validator import validate_email, EmailNotValidError

def validate_email_format(email):
    """Valider le format de l'email"""
    if not email or not email.strip():
        return False, "Email is required and cannot be empty"
    
    try:
        # Valider l'email avec email-validator
        valid = validate_email(email)
        return True, valid.email
    except EmailNotValidError as e:
        return False, "Invalid email format"

def validate_password_strength(password):
    """Valider la force du mot de passe"""
    if not password or not password.strip():
        return False, "Password is required and cannot be empty"
    
    # Regex pour mot de passe fort
    password_regex = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&.+])[A-Za-z\d@$!/\%*?&.+]{8,}$'
    
    if not re.match(password_regex, password):
        return False, "Password must be at least 8 characters long and include at least one uppercase letter, one lowercase letter, one number, and one special character"
    
    return True, "Password is valid"

def validate_username(username):
    """Valider le nom d'utilisateur"""
    if not username or not username.strip():
        return False, "Username is required and cannot be empty"
    
    if len(username) < 3:
        return False, "Username must be at least 3 characters long"
    
    if len(username) > 50:
        return False, "Username must be less than 50 characters"
    
    # Autoriser lettres, chiffres, tirets et underscores
    username_regex = r'^[a-zA-Z0-9_-]+$'
    if not re.match(username_regex, username):
        return False, "Username can only contain letters, numbers, hyphens and underscores"
    
    return True, "Username is valid"

def mask_email(email):
    """Masquer l'email pour la sécurité"""
    if not email or '@' not in email:
        return email
    
    username, domain = email.split('@')
    
    if len(username) <= 2:
        masked_username = username
    else:
        masked_username = username[0] + '*' * (len(username) - 2) + username[-1]
    
    if '.' in domain:
        domain_parts = domain.split('.')
        if len(domain_parts) >= 2:
            masked_domain = domain_parts[0][0] + '*' * (len(domain_parts[0]) - 1) + '.' + '.'.join(domain_parts[1:])
        else:
            masked_domain = domain
    else:
        masked_domain = domain[0] + '*' * (len(domain) - 1)
    
    return f"{masked_username}@{masked_domain}"

def is_valid_email(email):
    """Vérifier si l'email est valide (version simple)"""
    email_regex = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
    return bool(re.match(email_regex, email)) 