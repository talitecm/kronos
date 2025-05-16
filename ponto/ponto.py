from bibliotecas import *
from models.tabelas import db, Colaborador, Ponto

ponto_blueprint = Blueprint('ponto', __name__, template_folder='templates')

@ponto_blueprint.route('/', methods=['GET', 'POST'])

def registrar_ponto():
    if request.method == 'POST':
        matricula = request.form.get('matricula')
        senha = request.form.get('senha')

        if not matricula or not senha:
            flash("Matrícula e senha são obrigatórias.", "danger")
            return redirect(url_for('ponto.registrar_ponto'))

        # Busca colaborador pelo número de matrícula
        colaborador = Colaborador.query.filter_by(Matricula=matricula, Ativo=True).first()

        if not colaborador:
            flash("Matrícula não encontrada ou colaborador inativo.", "danger")
            return redirect(url_for('ponto.registrar_ponto'))

        # Verifica se a senha está correta
        if not colaborador.check_senha(senha):
            flash("Senha incorreta.", "danger")
            return redirect(url_for('ponto.registrar_ponto'))
        
        if colaborador.Nova_Senha:
            login_user(colaborador)
            return redirect(url_for('login.nova_senha'))  # Redireciona para troca de senha

        tz = pytz.timezone('America/Sao_Paulo')
        agora = datetime.now(tz)
        hoje = agora.date()

        # Último ponto do dia
        ultimo_ponto = Ponto.query.filter( Ponto.Matricula == matricula, 
        db.func.DATE(Ponto.Data_Hora) == hoje).order_by(Ponto.Data_Hora.desc()).first()

        # Define tipo de ponto
        if not ultimo_ponto or ultimo_ponto.Tipo == '0':
            tipo = '1'
            flash("Entrada registrada com sucesso!")
        else:
            tipo = '0'
            flash("Saída registrada com sucesso!")

        # Registra novo ponto
        novo_ponto = Ponto(
            Matricula=matricula,
            Tipo=tipo,
            Data_Hora=agora
        )
        db.session.add(novo_ponto)
        db.session.commit()

        return redirect(url_for('ponto.registrar_ponto'))

    # Se for GET, apenas retorna o formulário vazio
    return render_template("home.html")
