from flask import Blueprint, redirect, url_for, render_template, jsonify, g
from flask.ext.login import login_required

core = Blueprint('core', __name__, template_folder='templates')

@core.route('/', methods=['GET'])
def get_index():
    """ root path render main """
    return render_template('core/index.html')

@core.route('/test', methods=['GET'])
@login_required
def get_test():
    """ root path render main """
    return render_template('core/test.html')
