from utilidades import *            # Importando todas bibliotecas
from models.tabelas import *        # Importando tabela "Colaborador" do Banco de dados 

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

    conn = mysql.connector.connect(**config_bd)  # sua configuração de conexão
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT nome, matricula, cpf FROM colaborador 
        WHERE cpf = %s OR matricula = %s
    """
    cursor.execute(query, (cpf, matricula))
    colaborador = cursor.fetchone()

    cursor.close()
    conn.close()

    if colaborador:
        return jsonify(colaborador)
    else:
        return jsonify({'erro': 'Colaborador não encontrado.'}), 404