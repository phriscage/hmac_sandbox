#!/usr/bin/env python
"""
API user interface bootstrap file
"""
import sys
import os
import argparse
import logging
from flask import Flask, render_template, g, redirect, url_for
from flask.ext.login import LoginManager, current_user

sys.path.insert(0, os.path.dirname(
    os.path.realpath(__file__)) + '/../lib')
sys.path.insert(0, os.path.dirname(
    os.path.realpath(__file__)) + '/../conf')

from hmac_sandbox.v1.api.main import db_client
from hmac_sandbox.v1.lib.user.models import User

## put these in a config
API_URL = 'http://10.211.55.11:8000'
APP_SECRET_KEY = ('\xda\xe0\xff\xc8`\x99\x93e\xd0\xb9\x0e\xc9\xde\x84?q'
    '\x9e\x19\xc0\xa1\xa7\xfb\xd0\xde')

logger = logging.getLogger(__name__)

login_manager = LoginManager()

@login_manager.user_loader
def load_user(email_address):
    try:
        user = User(db_client=db_client, email_address=email_address)
    except ValueError as error:
        message = str(error)
        logger.warn(message)
        return None
    data = db_client.get(user.key, quiet=True)
    if not data.success:
        message = "'%s' does not exist." % email_address
        logger.warn(message)
        return None
    user.set_values(values=data.value)
    return user

def create_app():
    """ dynamically create the app """
    app = Flask(__name__, static_url_path='/static', static_folder='./static')
    app.config.from_object(__name__)
    app.secret_key = APP_SECRET_KEY
    login_manager.init_app(app)

    @app.before_request
    def before_request():
        g.user = current_user
        g.api_url = API_URL

    #@app.teardown_appcontext
    #def shutdown_session(exception=None):
        #db_session.remove()

    @app.errorhandler(401)
    def unauthorized_error_handle(error=None):
        """ handle all unauthorized_errors with redirect to login """
        return redirect(url_for('auth.login'))

    ## add each api Blueprint and create the base route
    from core.views import core
    app.register_blueprint(core, url_prefix="")
    from auth.views import auth
    app.register_blueprint(auth, url_prefix="/auth")
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
