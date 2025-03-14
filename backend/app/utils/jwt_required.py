from functools import wraps
from flask import request, jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity


def jwt_required():
    """
    Decorator para exigir token JWT válido
    """
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            try:
                verify_jwt_in_request()
                return fn(*args, **kwargs)
            except Exception as e:
                return jsonify({
                    "error": "invalid_token",
                    "message": "Token de acesso inválido ou expirado."
                }), 401
        return decorator
    return wrapper
