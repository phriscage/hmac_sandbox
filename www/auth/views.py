import os
import sys
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)) +
        '/../../../../../lib')
from hmac_sandbox.v1.api.main import db_client
from hmac_sandbox.v1.lib.user.models import User
from flask import Blueprint, request, redirect, url_for, render_template, g, \
    jsonify, session
from flask.ext.login import logout_user, current_user, login_user
import logging

logger = logging.getLogger(__name__)

auth = Blueprint('auth', __name__, template_folder='templates')

@auth.route('/login', methods=['GET', 'POST'])
def login(email_address=None, password=None):
    """ check if the request data exists with the correct values, then check
        if the User exists and the password matches else redirect to the
        signup page.
    """
    if request.method == 'POST':
        if request.content_type != 'application/json' or not request.data:
            message = "Content-Type: 'application/json' required"
            logger.warn(message)
            return jsonify(message=message, success=False), 400
        for var in ['email_address', 'password']:
            if var not in request.json:
                message = "'%s' required." % var
                return jsonify(message=message, success=False), 400
        try:
            user = User(db_client=db_client,
                email_address=request.json['email_address'])
        except ValueError as error:
            message = str(error)
            logger.warn(message)
            return jsonify(message=message, success=False), 400
        data = db_client.get(user.key, quiet=True)
        if not data.success:
            logger.warn("'%s' does not exist." % request.json['email_address'])
            message = "Unknown email_address or bad password"
            return jsonify(message=message, success=False), 400
        logger.debug("'%s' successfully found!" % request.json['email_address'])
        user.set_values(values=data.value)
        if not user.check_password(request.json['password']):
            logger.warn("'%s' incorrect password" % request.json['email_address'])
            message = "Unknown email_address or bad password"
            return jsonify(message=message, success=False), 400
        message = "'%s' successfully logged in!" % request.json['email_address']
        logger.info(message)
        ## don't return hashed password
        data.value.pop('password', None)
        login_user(user)
        return jsonify(url=url_for('core.get_promos'), success=True), 200
        #return redirect(url_for('core.get_index'))
    else:
        if g.user is not None and g.user.is_authenticated():
            return redirect(url_for('core.get_promos'))
        email_address = request.args.get('e')
        password = request.args.get('p')
        return render_template('auth/login.html', email_address=email_address, 
            password=password)

@auth.route('/logout', methods=['GET'])
def logout():
    """ logout the user and redirect to home """
    logout_user()
    session.pop('logged_in', None)
    return redirect(url_for('core.get_index'))
