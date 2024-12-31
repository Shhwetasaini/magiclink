import jwt
from datetime import datetime, timedelta
from django.conf import settings

def generate_jwt_token(user):
    expiration_time = datetime.utcnow() + timedelta(hours=24)
    payload = {
        'user_id': user.id,
        'exp': expiration_time,
        'iat': datetime.utcnow()
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
    return token
