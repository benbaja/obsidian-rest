import jwt
from uuid import uuid4
from flask import current_app

def generate_token(password):
    return jwt.encode(payload={'password': password, 'uuid': str(uuid4())}, key=current_app.secret_key, algorithm="HS256")