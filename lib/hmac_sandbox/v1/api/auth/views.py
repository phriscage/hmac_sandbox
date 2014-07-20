"""
    views file contains all the routes for the app and maps them to a
    specific hanlders function.
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)) +
        '/../../../../../lib')
from hmac_sandbox.v1.api.main import db_client
from hmac_sandbox.v1.lib.user.models import User
#from hmac_sandbox.v1.api.util import crossdomain
from hmac_sandbox.v1.api.lib.auth import requires_api_key, requires_hmac
from couchbase.exceptions import KeyExistsError
from flask import Blueprint, jsonify, request, abort, make_response
import json
import time
import logging

logger = logging.getLogger(__name__)

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['POST'])
def login():
    """ check if the request data exists with the correct values, then check 
        if the User exists and the password matches else return 404 
    """
    if not request.json:
        message = "must be application/json"
        logger.warn(message)
        return abort(400, message)
    for var in ['email_address', 'password']:
        if var not in request.json:
            message = "'%s' required." % var
            abort(400, message)
    try:
        user = User(db_client=db_client, 
            email_address=request.json['email_address'])
    except ValueError as error:
        message = str(error)
        logger.warn(message)
        return abort(400, message)
    data = db_client.get(user.key, quiet=True)
    if not data.success:
        logger.warn("'%s' does not exist." % request.json['email_address'])
        message = "Unknown email_address or bad password"
        abort(400, message)
    logger.debug("'%s' successfully found!" % request.json['email_address'])
    user.set_values(values=data.value)
    if not user.check_password(request.json['password']):
        logger.warn("'%s' incorrect password" % request.json['email_address'])
        message = "Unknown email_address or bad password"
        return abort(400, message)
    message = "'%s' successfully logged in!" % request.json['email_address']
    logger.info(message)
    ## don't return hashed password
    data.value.pop('password', None)
    return jsonify(message=message, data=data.value, success=True), 200
