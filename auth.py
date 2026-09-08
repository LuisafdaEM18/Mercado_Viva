import datetime
import jwt
from functools import wraps
from flask import Blueprint, request, jsonify, current_app
from werkzeug.security import check_password_hash
from models import Usuario

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/api/auth/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""

    if not username or not password:
        return jsonify({"error": "Usuario y contraseña son obligatorios."}), 400

    usuario = Usuario.query.filter_by(username=username).first()
    if not usuario or not check_password_hash(usuario.password_hash, password):
        return jsonify({"error": "Credenciales inválidas."}), 401

    exp = datetime.datetime.utcnow() + datetime.timedelta(
        minutes=current_app.config["JWT_EXP_MINUTES"]
    )
    token = jwt.encode(
        {"sub": usuario.id, "username": usuario.username, "exp": exp},
        current_app.config["SECRET_KEY"],
        algorithm="HS256",
    )

    return jsonify({"token": token, "nombre": usuario.nombre}), 200


def token_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Falta el token de autenticación."}), 401

        token = auth_header.split(" ", 1)[1]
        try:
            jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "El token ha expirado."}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Token inválido."}), 401

        return f(*args, **kwargs)

    return wrapper
