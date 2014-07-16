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
from hmac_sandbox.v1.api.auth import requires_api_key, requires_hmac
from couchbase.exceptions import KeyExistsError
## need to import all child models for now
from flask import Blueprint, jsonify, request, abort, make_response
import json
import time
import logging

logger = logging.getLogger(__name__)

users = Blueprint('users', __name__)

#create routes
@users.route('/new', methods=['POST', 'OPTIONS'])
#@crossdomain(origin="*", methods=['GET'], headers='Content-Type')
#@requires_api_key
def create():
    """create a user

    **Example request:**

    .. sourcecode:: http

       GET /users/new HTTP/1.1
       Accept: application/json
        data: { 'email_address': abc@abc.com }

    **Example response:**

    .. sourcecode:: http

       HTTP/1.1 200 OK
       Content-Type: application/json

    :statuscode 200: success
    :statuscode 400: bad data
    """
    if not request.json:
        message = "must be application json"
        logger.warn(message)
        return jsonify(message=message, success=False), 400
    try:
        user = User(db_client=db_client, **request.json)
    except ValueError as error:
        message = str(error)
        logger.warn(message)
        return jsonify(error=400, message=message, success=False), 400
    user.set_values()
    try:
        data = user.add()
    except KeyExistsError as error:
        message = "'%s' already exists." % user.key
        logger.warn(message)
        return jsonify(error=409, message=message, success=False), 409
    if not data.success:
        message = "Something broke... We are looking into it!"
        logger.critical(message)
        return jsonify(error=500, message=message, success=False), 500
    message = "'%s' added successfully!" % user.key
    logger.debug(message)
    return jsonify(message=message, success=True), 200


@users.route('/<email_address>', methods=['GET', 'OPTIONS'])
#@crossdomain(origin="*", methods=['GET'], headers='Content-Type')
@requires_api_key
#@requires_hmac
def get(email_address):
    """get a user

    **Example request:**

    .. sourcecode:: http

       GET /users/abc@abc.com HTTP/1.1
       Accept: application/json

    **Example response:**

    .. sourcecode:: http

       HTTP/1.1 200 OK
       Content-Type: application/json

    :statuscode 200: success
    :statuscode 400: bad data
    """
    try:
        user = User(db_client=db_client, email_address=email_address)
    except ValueError as error:
        message = str(error)
        logger.warn(message)
        return jsonify(error=400, message=message, success=False), 400
    data = db_client.get(user.key, quiet=True)
    if not data.success:
        message = "'%s' does not exist." % email_address
        logger.warn(message)
        return jsonify(error=404, message=message, success=False), 404
    message = "'%s' successfully found!" % email_address
    logger.debug(message)
    ## don't display the client and group data yet
    for attr in ['clients', 'groups']:
        data.value.pop(attr, None)
    return jsonify(message=message, data=data.value, success=True), 200

