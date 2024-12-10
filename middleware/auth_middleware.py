import jwt
from flask import request, jsonify
from functools import wraps
from config import Config
import datetime

def generate_token(user_data):
    """Fungsi untuk membuat token dengan masa berlaku 5 menit."""
    payload = {
        **user_data,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=1)
    }
    token = jwt.encode(payload, Config.JWT_SECRET, algorithm="HS256")
    return token

def authenticate_token(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"error": True, "message": "Token missing"}), 401

        token = auth_header.split(" ")[1]
        try:
            user = jwt.decode(token, Config.JWT_SECRET, algorithms=["HS256"])
            request.user = user  # Menyimpan data pengguna ke request
        except jwt.ExpiredSignatureError:
            return jsonify({"error": True, "message": "Token expired"}), 403
        except jwt.InvalidTokenError:
            return jsonify({"error": True, "message": "Invalid token"}), 403
        return func(*args, **kwargs)
    return wrapper
