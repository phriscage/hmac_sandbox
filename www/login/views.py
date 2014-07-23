from flask import Blueprint, request, redirect, url_for, render_template, \
    jsonify

login = Blueprint('login', __name__, template_folder='templates')

@login.route('', methods=['GET'])
def get_index(email_address=None, password=None):
    """ root path render main """
    email_address = request.args.get('e')
    password = request.args.get('p')
    return render_template('login/index.html', email_address=email_address, 
        password=password)
