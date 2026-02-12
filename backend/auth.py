from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from flask import request, jsonify
from models import User
from db import db

login_manager = LoginManager()
bcrypt = Bcrypt()


def init_auth(app):
    login_manager.init_app(app)
    bcrypt.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))


# =========================
# REGISTER FUNCTION
# =========================

def register_user():
    data = request.json

    if not data.get("username") or not data.get("password"):
        return jsonify({"error": "Username and password required"}), 400

    existing_user = User.query.filter_by(username=data["username"]).first()

    if existing_user:
        return jsonify({"error": "Username already exists"}), 400

    hashed_password = bcrypt.generate_password_hash(
        data["password"]
    ).decode("utf-8")

    new_user = User(
        username=data["username"],
        password=hashed_password
    )

    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201


# =========================
# LOGIN FUNCTION
# =========================

def login_user_route():
    data = request.json

    user = User.query.filter_by(username=data["username"]).first()

    if not user:
        return jsonify({"error": "User not found"}), 404

    if bcrypt.check_password_hash(user.password, data["password"]):
        login_user(user)
        return jsonify({"message": "Login successful", "user_id": user.id}), 200

    return jsonify({"error": "Invalid credentials"}), 401


# =========================
# LOGOUT FUNCTION
# =========================

@login_required
def logout_user_route():
    logout_user()
    return jsonify({"message": "Logged out successfully"}), 200
