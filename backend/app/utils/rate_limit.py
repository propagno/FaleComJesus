import time
import redis
from flask import request, jsonify, current_app
from functools import wraps


class RateLimiter:
    """Rate limiting using Redis for distributed rate limiting"""

    def __init__(self, redis_client=None):
        self.redis = redis_client

    def _get_redis(self):
        """Get Redis client from app or use existing one"""
        if self.redis:
            return self.redis

        if 'redis' in current_app.extensions:
            return current_app.extensions['redis']

        # If we don't have Redis available, use a local in-memory implementation
        # Note: This is not suitable for production with multiple workers
        return None

    def limit(self, key_prefix, limit=100, period=60):
        """
        Rate limiting decorator

        Args:
            key_prefix: Prefix for the rate limiting key (e.g., 'api_request')
            limit: Max number of requests allowed in the period
            period: Time period in seconds
        """
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                # Get client identifier (IP or user ID if authenticated)
                client_id = self._get_client_id()
                key = f"{key_prefix}:{client_id}"

                # Check rate limit
                redis_client = self._get_redis()
                if redis_client:
                    # Use Redis-based rate limiting if available
                    current = self._check_redis_rate_limit(
                        redis_client, key, period)
                    if current > limit:
                        return jsonify({
                            'error': 'Too many requests',
                            'message': f'Rate limit exceeded. Try again in {period} seconds.'
                        }), 429
                else:
                    # Fallback to memory-based rate limiting
                    if not hasattr(self, '_memory_rate_limit'):
                        self._memory_rate_limit = {}

                    if not self._check_memory_rate_limit(key, limit, period):
                        return jsonify({
                            'error': 'Too many requests',
                            'message': f'Rate limit exceeded. Try again in {period} seconds.'
                        }), 429

                # Execute the original function
                return f(*args, **kwargs)

            return decorated_function

        return decorator

    def _get_client_id(self):
        """Get client identifier"""
        # Use user ID if authenticated
        if hasattr(request, 'user_id') and request.user_id:
            return str(request.user_id)

        # Fallback to IP address
        return request.remote_addr or 'unknown'

    def _check_redis_rate_limit(self, redis_client, key, period):
        """Check rate limit using Redis"""
        current_time = int(time.time())
        # Clear old requests from the window
        redis_client.zremrangebyscore(key, 0, current_time - period)
        # Add current request
        redis_client.zadd(key, {str(current_time): current_time})
        # Set expiry on the key
        redis_client.expire(key, period)
        # Get current count
        return redis_client.zcard(key)

    def _check_memory_rate_limit(self, key, limit, period):
        """Check rate limit using in-memory storage (fallback)"""
        current_time = time.time()

        # Initialize data structures if key doesn't exist
        if key not in self._memory_rate_limit:
            self._memory_rate_limit[key] = []

        # Remove old timestamps
        self._memory_rate_limit[key] = [
            ts for ts in self._memory_rate_limit[key]
            if current_time - ts < period
        ]

        # Check if we're over the limit
        if len(self._memory_rate_limit[key]) >= limit:
            return False

        # Add current timestamp
        self._memory_rate_limit[key].append(current_time)
        return True


# Singleton instance for use in the app
rate_limiter = RateLimiter()


# Convenience decorator for route rate limiting
def rate_limit(limit=100, period=60, key_prefix='route'):
    """
    Rate limiting decorator for routes

    Args:
        limit: Max number of requests allowed in the period
        period: Time period in seconds
        key_prefix: Prefix for the rate limiting key
    """
    return rate_limiter.limit(key_prefix, limit, period)
