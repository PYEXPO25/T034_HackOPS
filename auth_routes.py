from flask import Blueprint, request, jsonify, session
from firebase_admin import auth
from db_operations import save_progress, get_progress

auth_bp = Blueprint("auth", __name__)  # Define a Blueprint

@auth_bp.route("/signup", methods=["POST"])
def signup():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    try:
        user = auth.create_user(email=email, password=password)
        return jsonify({"message": "Signup successful!", "uid": user.uid}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    try:
        user = auth.get_user_by_email(email)
        session["user"] = user.uid
        return jsonify({"message": "Login successful!"}), 200
    except Exception as e:
        return jsonify({"error": "Invalid credentials"}), 401

@auth_bp.route("/logout", methods=["POST"])
def logout():
    session.pop("user", None)
    return jsonify({"message": "Logged out successfully!"}), 200

@auth_bp.route("/save_progress", methods=["POST"])
def save_user_progress():
    if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json
    score = data.get("score")
    streak = data.get("streak")

    if score is None or streak is None:
        return jsonify({"error": "Missing score or streak"}), 400

    response = save_progress(session["user"], score, streak)
    return jsonify(response)

@auth_bp.route("/get_progress", methods=["GET"])
def get_user_progress():
    if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    response = get_progress(session["user"])
    return jsonify(response)
