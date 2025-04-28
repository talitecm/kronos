from flask import Blueprint, render_template

adm_blueprint = Blueprint('adm', __name__, template_folder='templates')

@adm_blueprint.route('/login')
def login():
    return render_template('login.html')

@adm_blueprint.route('/adm')
def adm():
    return render_template('adm.html')