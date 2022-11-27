from django.core.exceptions import ValidationError
from uuid import UUID


def validate_password(password):

    if len(password) < 7:
        raise ValidationError('Hasło za krótkie')

    if len(password) > 64:
        raise ValidationError('Hasło za długie')

    contains_lower_char = False
    contains_upper_char = False
    
    for char in password:
        if char.islower():
            contains_lower_char = True
            break
    for char in password:
        if char.isupper():
            contains_upper_char = True
            break
    
    if (contains_lower_char is False) or (contains_upper_char is False):
        raise ValidationError('Hasło musi zawierać małe i duże litery')

    if not any([char.isdigit() for char in password]):
        raise ValidationError('Hasło musi zawierać minimum jedną cyfrę')

    special_char = """!@#$%^&*()_+-={}[]|\:";'<>?,./"""
    contains_special_char = False
    
    for char in special_char:
        if char in password:
            contains_special_char = True
            break
    
    if contains_special_char is False:
        raise ValidationError(f'Hasło musi zawierać znak specjalny {special_char}')


def validate_token(token):

    try:
        uuid_obj = UUID(token, version=4)
    except ValueError:
        return False
    
    return str(uuid_obj) == token