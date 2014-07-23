#!/usr/bin/env python
"""
API bootstrap file
"""
from flask import Flask, render_template
import sys
import os
import argparse
import logging

sys.path.insert(0, os.path.dirname(
    os.path.realpath(__file__)) + '/../lib')
sys.path.insert(0, os.path.dirname(
    os.path.realpath(__file__)) + '/../conf')

logger = logging.getLogger(__name__)

def create_app():
    """ dynamically create the app """
    app = Flask(__name__, static_url_path='/static', static_folder='./static')
    app.config.from_object(__name__)

    #@app.teardown_appcontext
    #def shutdown_session(exception=None):
        #db_session.remove()

    @app.errorhandler(400)
    @app.errorhandler(401)
    @app.errorhandler(404)
    @app.errorhandler(405)
    @app.errorhandler(500)
    def default_error_handle(error=None):
        """ handle all errors with correct html output """
        return render_template('%s.html' % error.code), error.code

    ## add each api Blueprint and create the base route
    from core.views import core
    app.register_blueprint(core, url_prefix="/")
    from login.views import login
    app.register_blueprint(login, url_prefix="/login")
    #from lvd.v1.api.account_numbers.views import account_numbers
    #app.register_blueprint(account_numbers, url_prefix="/account_numbers")

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
        dest="port", type=int, default=8080)
    kwargs = parser.parse_args()
    bootstrap(**kwargs.__dict__)
