#!/usr/bin/env python
"""
API bootstrap file
"""
from flask import Flask, jsonify
import sys
import os
import argparse
import logging
from couchbase import Couchbase
from couchbase.exceptions import ConnectError

sys.path.insert(0, os.path.dirname(
    os.path.realpath(__file__)) + '/../../../../lib')
sys.path.insert(0, os.path.dirname(
    os.path.realpath(__file__)) + '/../../../../conf')

import hmac_sandbox
## put these in a config
COUCHBASE_HOST = 'localhost'
COUCHBASE_PORT = '8091'
COUCHBASE_BUCKET = 'hmac_sandbox'

logger = logging.getLogger(__name__)

def connect_db():
    """ connect to couchbase """
    global db_client
    try:
        db_client = Couchbase.connect(
            host=COUCHBASE_HOST,
            port=COUCHBASE_PORT,
            bucket=COUCHBASE_BUCKET)
    except ConnectError as error:
        raise
    return db_client

db_client = connect_db()


def create_app():
    """ dynamically create the app """
    #app = Flask(__name__, static_url_path='')
    app = Flask(__name__)
    app.config.from_object(__name__)

    #@app.teardown_appcontext
    #def shutdown_session(exception=None):
        #db_session.remove()

    @app.errorhandler(400)
    @app.errorhandler(404)
    @app.errorhandler(405)
    @app.errorhandler(500)
    def default_error_handle(error=None):
        """ handle all errors with json output """
        return jsonify(error=error.code, message=str(error), success=False),\
            error.code

    ## add each api Blueprint and create the base route
    from hmac_sandbox.v1.api.users.views import users
    app.register_blueprint(users, url_prefix="/v1/users")
    from hmac_sandbox.v1.api.events.views import events
    app.register_blueprint(events, url_prefix="/v1/events")

    return app


def bootstrap(**kwargs):
    """bootstraps the application. can handle setup here"""
    app = create_app()
    app.debug = True
    app.run(host=kwargs['host'], port=kwargs['port'])


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format=("%(asctime)s %(levelname)s %(name)s[%(process)s] : %(funcName)s"
            " : %(message)s"),
        #filename='/var/log/AAA/%s.log' % FILE_NAME
    )
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", help="Hostname or IP address",
        dest="host", type=str, default='0.0.0.0')
    parser.add_argument("--port", help="Port number",
        dest="port", type=int, default=8000)
    kwargs = parser.parse_args()
    bootstrap(**kwargs.__dict__)
