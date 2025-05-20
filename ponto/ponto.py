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
                flash("Último ponto apagado. Tente registrar novamente em 15s.", "warning")
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

@ponto_blueprint.route('/relatorio_colaborador', methods=['GET', 'POST'])
def relatorio_colaborador():
    matricula = ''
    senha = ''
    data_inicio = ''
    data_fim = ''

    if request.method == 'POST':
        matricula = request.form.get('matricula')
        senha = request.form.get('senha')
        data_inicio = request.form.get('data_inicio')
        data_fim = request.form.get('data_fim')

        if not matricula or not senha:
            flash("Matrícula e senha são obrigatórias.", "danger")
        else:
            colaborador = Colaborador.query.filter_by(Matricula=matricula).first()

            if not colaborador:
                flash("Colaborador não encontrado.", "danger")
            elif not colaborador.check_senha(senha):
                flash("Senha incorreta.", "danger")
            else:
                # Se validado, redireciona direto para o PDF com os parâmetros
                pdf_url = url_for('ponto.relatorio_colaborador_pdf',
                                  matricula=matricula,
                                  senha=senha,
                                  data_inicio=data_inicio,
                                  data_fim=data_fim)
                return redirect(pdf_url)

    return render_template(
        'relatorio_colaborador.html'
    )

@ponto_blueprint.route('/relatorio_colaborador/pdf')
def relatorio_colaborador_pdf():
    matricula = request.args.get('matricula')
    senha = request.args.get('senha')
    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')

    if not matricula or not senha:
        return "Acesso negado: matrícula e senha são obrigatórias.", 400

    colaborador = Colaborador.query.filter_by(Matricula=matricula).first()

    if not colaborador:
        return "Colaborador não encontrado.", 404

    if not colaborador.check_senha(senha):
        return "Senha incorreta.", 403

    query = Ponto.query.filter(Ponto.Matricula == matricula)

    try:
        if data_inicio:
            inicio = datetime.strptime(data_inicio, '%Y-%m-%d')
            query = query.filter(Ponto.Data_Hora >= inicio)

        if data_fim:
            fim = datetime.strptime(data_fim, '%Y-%m-%d') + timedelta(days=1)
            query = query.filter(Ponto.Data_Hora < fim)

    except ValueError:
        pass  # Erro de data inválida, ignora filtro

    pontos = query.order_by(Ponto.Data_Hora.desc()).all()

    nome_colaborador = colaborador.Nome
    data_atual = datetime.now()

    html = render_template("pdf.html", 
                           pontos=pontos, 
                           matricula=matricula, 
                           nome=nome_colaborador,
                           data_atual=data_atual)

    pdf = HTML(string=html).write_pdf()

    return Response(pdf, mimetype='application/pdf',
                    headers={'Content-Disposition': 'inline; filename=relatorio_pontos_colaborador.pdf'})


