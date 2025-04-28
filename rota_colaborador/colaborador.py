from flask import Blueprint, render_template

colaborador_blueprint = Blueprint('colaborador', __name__, template_folder='templates')

@colaborador_blueprint.route('/')
def home():
    return render_template('home.html')