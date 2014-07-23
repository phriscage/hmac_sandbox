from flask import Blueprint, redirect, url_for, render_template, jsonify

core = Blueprint('core', __name__, template_folder='templates')

@core.route('', methods=['GET'])
def get_index():
    """ root path render main """
    return render_template('index.html')
