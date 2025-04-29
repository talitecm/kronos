from utilidades import *            # Importando todas bibliotecas
from models.tabelas import *        # Importando tabela "Colaborador" do Banco de dados 

adm_blueprint = Blueprint('adm', __name__, template_folder='templates')

@adm_blueprint.route('/adm')
@login_required
def adm():
    return render_template('adm.html')