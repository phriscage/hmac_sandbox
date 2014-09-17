from flask import Blueprint, request, redirect, url_for, render_template, g, \
    jsonify, session
from flask.ext.login import login_required

core = Blueprint('core', __name__, template_folder='templates')

@core.route('/', methods=['GET'])
def get_index():
    """ root path render main """
    if g.user is not None and g.user.is_authenticated():
        return redirect(url_for('core.get_promos'))
    first_name = request.args.get('f')
    last_name = request.args.get('l')
    email_address = request.args.get('e')
    return render_template('core/index.html', first_name=first_name,
        last_name=last_name, email_address=email_address)

@core.route('/test', methods=['GET'])
@login_required
def get_test():
    """ root path render main """
    return render_template('core/test.html')

@core.route('/promos', methods=['GET'])
@login_required
def get_promos():
    """ promos render top promos """
    return render_template('core/promos.html')

@core.route('/profile', methods=['GET'])
@login_required
def get_profile():
    """ profile render """
    return render_template('core/profile.html')
