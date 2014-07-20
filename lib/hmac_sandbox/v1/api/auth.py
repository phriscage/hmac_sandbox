"""API Authentication methods"""

from flask import request, abort
from functools import wraps
from hmac_sandbox.v1.lib.auth import verify_client, verify_token
import logging

API_AUTH_ENABLED = True

logger = logging.getLogger(__name__)

def auth_enabled():
    """simple getter for auth detection. use in test cases to disable auth"""
    return API_AUTH_ENABLED


def requires_api_key(func):
    """Decorator to force api key authentication on any route. Requires a valid
        api key to allow access. You can configure auth check by setting
        API_AUTH_ENABLED = True/False in the configuration object.

        Returns:
            400 Bad Request if params missing
            401 Authorization Required if not authorized
    """
    @wraps(func)
    def api_key_wrapper(*args, **kwargs):
        """Wrapper method"""
        logger.debug(request.headers)
        if auth_enabled():
            api_key = request.headers.get('Api-Key')
            data = request.data
            if api_key is None or not api_key:
                message = "Api-Key is required"
                logger.warn(message)
                abort(400, message)
            client = verify_client(api_key)
            if not client:
                logger.warn("client DNE: '%s'" % api_key)
                abort(401)
            kwargs['client'] = client
        return func(*args, **kwargs)
    return api_key_wrapper

def requires_hmac(func):
    """Decorator to force hmac authentication on any route. Requires a valid
        client and hmac hash to allow access. You can configure auth check
        by setting API_AUTH_ENABLED = True/False in the configuration object.

        Returns:    
            400 Bad Request if params missing
            401 Authorization Required if not authorized
    """
    @wraps(func)
    def hmac_wrapper(*args, **kwargs):
        """Wrapper method"""
        logger.debug(request.headers)
        if auth_enabled():
            api_key = request.headers.get('Api-Key')
            hmac_hash = request.headers.get('Hmac-hash')
            data = request.data
            if hmac_hash is None or not hmac_hash:
                message = "HMAC-Hash is required"
                logger.warn(message)
                abort(400, message)
            if api_key is None or not api_key:
                message = "Api-Key is required"
                logger.warn(message)
                abort(400, message)
            client = verify_client(api_key)
            if not client:
                logger.warn("client DNE: '%s'" % api_key)
                abort(401)
            kwargs['client'] = client
            if not verify_token(client.value.get('api_secret'), data, data):
                logger.warn("client unauthorized: '%s'" % client.value)
                abort(401)
        return func(*args, **kwargs)
    return hmac_wrapper

