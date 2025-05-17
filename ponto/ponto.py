from bibliotecas import *
from models.tabelas import db, Colaborador, Ponto

ponto_blueprint = Blueprint('ponto', __name__, template_folder='templates')
from datetime import datetime, timedelta
import pytz

@ponto_blueprint.route('/', methods=['GET', 'POST'])
def registrar_ponto():
    tz = pytz.timezone('America/Sao_Paulo')
    agora = datetime.now(tz)
    hoje = agora.date()

    if request.method == 'POST':
        matricula = request.form.get('matricula')
        senha = request.form.get('senha')

        if not matricula or not senha:
            flash("Matrícula e senha são obrigatórias.", "danger")
            return redirect(url_for('ponto.registrar_ponto'))

        colaborador = Colaborador.query.filter_by(Matricula=matricula, Ativo=True).first()

        if not colaborador:
            flash("Matrícula não encontrada ou colaborador inativo.", "danger")
            return redirect(url_for('ponto.registrar_ponto'))

        if not colaborador.check_senha(senha):
            flash("Senha incorreta.", "danger")
            return redirect(url_for('ponto.registrar_ponto'))

        # Busca todos os pontos do dia (ordenados do mais recente para o mais antigo)
        pontos_do_dia = Ponto.query.filter(
            Ponto.Matricula == matricula,
            db.func.DATE(Ponto.Data_Hora) == hoje
        ).order_by(Ponto.Data_Hora.desc()).all()

        if pontos_do_dia:
            ultimo_ponto = pontos_do_dia[0]  # O mais recente
            data_hora_ultimo = ultimo_ponto.Data_Hora

            # Força fuso horário, se necessário
            if data_hora_ultimo.tzinfo is None:
                data_hora_ultimo = tz.localize(data_hora_ultimo)

            diferenca_segundos = (agora - data_hora_ultimo).total_seconds()

            if diferenca_segundos < 60:
                db.session.delete(ultimo_ponto)
                db.session.commit()
                flash("Último ponto apagado por ser muito próximo ao anterior.", "warning")
                return redirect(url_for('ponto.registrar_ponto'))

        # Define tipo do novo ponto
        if not pontos_do_dia:
            tipo = '1'
            flash("Entrada registrada!", "success")
        else:
            ultimo_tipo = pontos_do_dia[0].Tipo
            if ultimo_tipo == '1':
                tipo = '0'
                flash("Saída registrada!", "success")
            else:
                tipo = '1'
                flash("Nova entrada registrada.", "success")

        # Registra novo ponto
        novo_ponto = Ponto(
            Matricula=matricula,
            Tipo=tipo,
            Data_Hora=agora
        )

        db.session.add(novo_ponto)
        db.session.commit()

        return redirect(url_for('ponto.registrar_ponto'))

    return render_template("home.html")