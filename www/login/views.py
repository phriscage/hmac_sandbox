from flask import Blueprint, request, redirect, url_for, render_template, \
    jsonify

login = Blueprint('login', __name__, template_folder='templates')

@login.route('', methods=['GET'])
def get_index():
    """ root path render main """
    return render_template('login/index.html')
