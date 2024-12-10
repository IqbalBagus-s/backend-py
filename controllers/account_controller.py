import jwt
import redis
from flask import request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config
import datetime
import re
from models.user_history_model import find_user_by_email, create_user, get_histories_by_user_id, update_user_profile, find_user_by_id, find_user_by_name

def register_user():
    data = request.get_json()
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    # Validasi panjang username, email, dan password
    if len(name) < 8 or len(email) < 8 or len(password) < 8:
        return jsonify({"error": True, "message": "Username or password must be at least 8 characters long"}), 400

    # Validasi format email menggunakan regex
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_regex, email):
        return jsonify({"error": True, "message": "Invalid email format"}), 400

    # Cek apakah email sudah terdaftar
    if find_user_by_email(email):
        return jsonify({"error": True, "message": "Email is already registered"}), 400

    # Hash password dan simpan user baru
    hashed_password = generate_password_hash(password)
    create_user(name, email, hashed_password)
    
    return jsonify({"error": False, "message": "User created"})

def login_user():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    user = find_user_by_email(email)
    if not user or not check_password_hash(user[3], password):  # Assuming password is in column 3
        return jsonify({"error": True, "message": "Invalid email or password"}), 400

    token = jwt.encode({"userId": user[0], "name": user[1]}, Config.JWT_SECRET, algorithm="HS256")
    return jsonify({"error": False, "message": "Login successful", "token": token})

# Fungsi untuk mendapatkan profil pengguna
def get_profile():
    user_id = request.user["userId"]  # Mendapatkan user_id dari token
    user = find_user_by_id(user_id)  # Cari pengguna berdasarkan ID

    if not user:
        return jsonify({"error": True, "message": "User not found"}), 404

    # Mengembalikan profil pengguna
    return jsonify({
        "error": False,
        "user": {
            "name": user[1],
            "email": user[2],
        }
    })

def update_profile():
    user_id = request.user["userId"]  # Mendapatkan userId dari token JWT
    data = request.get_json()
    name = data.get("name")
    password = data.get("password")

    # Cek jika ada input untuk diperbarui
    if not name and not password:
        return jsonify({"error": True, "message": "At least one field (name or password) must be provided"}), 400
    
    # Cek jika nama atau password yang diberikan kosong
    if name == "" or password == "":
        return jsonify({"error": True, "message": "Name and password cannot be empty"}), 400

    # Jika ada nama yang ingin diubah
    if name:
        if len(name) < 8:
            return jsonify({"error": True, "message": "Username must be at least 8 characters long"}), 400
        
        # Cek apakah ada pengguna lain yang menggunakan nama ini
        existing_user = find_user_by_name(name)
        if existing_user and existing_user[0] != user_id:  # Pastikan bukan milik pengguna yang sama
            return jsonify({"error": True, "message": "Username is already taken"}), 400

    # Jika ada password yang ingin diubah
    if password:
        if len(password) < 8:
            return jsonify({"error": True, "message": "Password must be at least 8 characters long"}), 400
        hashed_password = generate_password_hash(password)  # Hash password baru

    # Ambil data pengguna yang ada
    user = find_user_by_id(user_id)
    if not user:
        return jsonify({"error": True, "message": "User not found"}), 404

    # Jika tidak ada perubahan pada nama, gunakan nama lama, dan jika tidak ada perubahan pada password, gunakan password lama
    new_name = name if name else user[1]
    new_password = hashed_password if password else user[2]

    # Perbarui profil
    update_result = update_user_profile(user_id, new_name, new_password)

    if update_result:
        return jsonify({"error": False, "message": "Profile updated successfully"})
    else:
        return jsonify({"error": True, "message": "Failed to update profile"}), 400


def get_histories():
    user_id = request.user["userId"]
    histories = get_histories_by_user_id(user_id)
    if not histories:
        return jsonify({"error": True, "message": "No history found"}), 404
    return jsonify({"error": False, "histories": histories})

# Inisialisasi Redis
redis_client = redis.StrictRedis(host='localhost', port=6379, decode_responses=True)

def logout_user():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"error": True, "message": "Token missing"}), 401

    token = auth_header.split(" ")[1]
    try:
        # Decode token untuk mendapatkan waktu kedaluwarsa
        decoded_token = jwt.decode(token, Config.JWT_SECRET, algorithms=["HS256"], options={"verify_exp": False})
        exp_time = decoded_token.get("exp")
        if not exp_time:
            return jsonify({"error": True, "message": "Invalid token"}), 400

        # Simpan token ke Redis dengan waktu kedaluwarsa
        ttl = exp_time - int(datetime.utcnow().timestamp())
        redis_client.setex(f"blacklist:{token}", ttl, "true")

        return jsonify({"error": False, "message": "Logged out successfully"})
    except jwt.ExpiredSignatureError:
        return jsonify({"error": True, "message": "Token already expired"}), 400
    except jwt.InvalidTokenError:
        return jsonify({"error": True, "message": "Invalid token"}), 400

