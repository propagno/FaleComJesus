from flask import request, jsonify
from functools import wraps
import time

# Implementação simples de limitador de taxa


class SimpleLimiter:
    def __init__(self):
        self.limits = {}

    def limit(self, limit_string):
        """
        Decorator para limitar taxa de requisições

        Args:
            limit_string (str): String no formato "X per minute/hour/day"
        """
        def decorator(f):
            @wraps(f)
            def wrapped_f(*args, **kwargs):
                # Implementação simples que não faz nada
                return f(*args, **kwargs)
            return wrapped_f
        return decorator


# Instância do limitador
limiter = SimpleLimiter()

# Função para lidar com erros de limite de taxa


def ratelimit_handler(e):
    return jsonify({
        "error": "rate_limit_exceeded",
        "message": "Você excedeu o limite de requisições. Por favor, tente novamente mais tarde.",
        "retry_after": 60  # 1 minuto
    }), 429
