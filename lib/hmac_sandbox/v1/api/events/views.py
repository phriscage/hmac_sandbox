"""
    views file contains all the routes for the app and maps them to a
    specific hanlders function.
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)) +
        '/../../../../../lib')
from hmac_sandbox.v1.api.main import db_client
from hmac_sandbox.v1.lib.event.models import Event
#from hmac_sandbox.v1.api.util import crossdomain
from couchbase.exceptions import KeyExistsError
## need to import all child models for now
from flask import Blueprint, jsonify, request, abort, make_response
import json
import time
import logging

logger = logging.getLogger(__name__)

events = Blueprint('events', __name__)

#create routes
@events.route('/new', methods=['POST', 'OPTIONS'])
#@crossdomain(origin="*", methods=['GET'], headers='Content-Type')
#@requires_api_key
def create():
    """create a event

    **Example request:**

    .. sourcecode:: http

       GET /events/new HTTP/1.1
       Accept: application/json
        data: {
            "name":"odometer",
            "value":43572.738281,
            "timestamp":1362060000.036000
        }

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
        event = Event(db_client=db_client, **request.json)
    except ValueError as error:
        message = str(error)
        logger.warn(message)
        return jsonify(error=400, message=message, success=False), 400
    event.set_values(request.json)
    try:
        data = event.add()
    except KeyExistsError as error:
        message = "'%s' already exists." % event.key
        logger.warn(message)
        return jsonify(error=409, message=message, success=False), 409
    if not data.success:
        message = "Something broke... We are looking into it!"
        logger.critical(message)
        return jsonify(error=500, message=message, success=False), 500
    message = "'%s' added successfully!" % event.key
    logger.debug(message)
    return jsonify(message=message, success=True), 200
