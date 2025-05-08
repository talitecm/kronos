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
        # Verifica se o colaborador é administrador
        email = colaborador.administrador.Email if hasattr(colaborador, 'administrador') and colaborador.administrador else ''
        administrador = bool(colaborador.administrador)

        return jsonify({
            'nome': colaborador.Nome,
            'matricula': colaborador.Matricula,
            'email': email or None,
            'administrador': administrador,
            'ativo': colaborador.Ativo
        })
    else:
        logging.warning(f"Colaborador NÃO encontrado com matrícula: {matricula}")
        return jsonify({'erro': 'Colaborador não encontrado.'}), 404
    
@adm_blueprint.route('/editar', methods=['POST'])
@login_required
def salvar_edicao():
    dados = request.get_json()
    matricula = dados.get('matricula')
    nome = dados.get('nome')
    ativo = dados.get('ativo') == '1'
    administrador = dados.get('administrador') == '1'

    colaborador = Colaborador.query.filter_by(Matricula=matricula).first()

    if not colaborador:
        return jsonify({'erro': 'Colaborador não encontrado.'}), 404

    try:
        # Atualiza campos básicos
        colaborador.Nome = nome
        colaborador.Ativo = ativo

        # Se for administrador e ainda não existe, cria
        if administrador and not colaborador.administrador:
            novo_admin = Administrador(
                Matricula=colaborador.Matricula,
                Idadministrador=nome,
                Email=f"{nome.lower().replace(' ', '.')}@empresa.com",
                Senha="padrao123"
            )
            db.session.add(novo_admin)

        # Se NÃO é mais administrador, remove
        elif not administrador and colaborador.administrador:
            db.session.delete(colaborador.administrador)

        db.session.commit()
        return jsonify({'sucesso': True})

    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': f'Erro ao salvar: {str(e)}'}), 500
    
@adm_blueprint.route('/editar/<matricula>')
@login_required
def editar_colaborador(matricula):
    colaborador = Colaborador.query.filter_by(Matricula=matricula).first()

    if not colaborador:
        return jsonify({'erro': 'Colaborador não encontrado.'}), 404

    return jsonify({
        'matricula': colaborador.Matricula,
        'nome': colaborador.Nome,
        'email': colaborador.administrador.Email if colaborador.administrador else '',
        'administrador': bool(colaborador.administrador),
        'ativo': colaborador.Ativo
    })