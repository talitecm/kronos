from utilidades import *            # Importando todas bibliotecas
from models.tabelas import *        # Importando tabelas do Banco de dados 

adm_blueprint = Blueprint('adm', __name__, template_folder='templates')

@adm_blueprint.route('/adm')
@login_required
def adm():
    return render_template('adm.html')

@adm_blueprint.route('/adm/consultar', methods=['POST'])
@login_required
def consultar_colaborador():
    dados = request.get_json()
    matricula = dados.get('matricula')

    if not matricula:
        return jsonify({'erro': 'Matrícula vazia.'}), 400

    logging.info(f"Tentando buscar colaborador com matrícula: {matricula}")

    colaborador = Colaborador.query.filter_by(Matricula=matricula).first()

    if colaborador:
        logging.info(f"Colaborador encontrado: {colaborador.Nome}")
        return jsonify({
            'nome': colaborador.Nome,
            'matricula': colaborador.Matricula,
            'ativo': colaborador.Ativo
        })
    else:
        logging.warning(f"Colaborador NÃO encontrado com matrícula: {matricula}")
        return jsonify({'erro': 'Colaborador não encontrado.'}), 404