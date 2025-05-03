from utilidades import *
from models.tabelas import db, Colaborador, Ponto

ponto_blueprint = Blueprint('ponto', __name__, template_folder='templates', static_folder='static')

@ponto_blueprint.route('/', methods=['GET', 'POST'])

def registrar_ponto():
    matricula = request.form.get('matricula')

    if request.method == 'POST':
        if not matricula:
            return render_template("home.html", mensagem="Matrícula não informada.")

        # Busca colaborador pelo número de matrícula
        colaborador = Colaborador.query.filter_by(Matricula=matricula, Ativo=True).first()

        if not colaborador:
            return render_template("home.html", mensagem="Matrícula não encontrada ou colaborador inativo.")

        hoje = date.today()

        # Último ponto do dia
        ultimo_ponto = Ponto.query.filter(
            Ponto.Matricula == matricula,
            db.func.DATE(Ponto.Data_Hora) == hoje
        ).order_by(Ponto.Data_Hora.desc()).first()

        # Define tipo de ponto
        if not ultimo_ponto or ultimo_ponto.Tipo == '0':
            tipo = '1'
            mensagem = "Entrada registrada com sucesso!"
        else:
            tipo = '0'
            mensagem = "Saída registrada com sucesso!"

        # Registra novo ponto
        novo_ponto = Ponto(Matricula=matricula, Tipo=tipo)
        db.session.add(novo_ponto)
        db.session.commit()

        return render_template("home.html", mensagem=mensagem)

    # Se for GET, apenas retorna o formulário vazio
    return render_template("home.html")