from flask import Blueprint, render_template, request
from flask.ext.login import login_required

core = Blueprint('core', __name__, template_folder='templates')

@core.route('/', methods=['GET'])
def get_index():
    """ root path render main """
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
