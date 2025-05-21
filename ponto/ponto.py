from bibliotecas import *                           # Puxando as bibliotecas necessárias
from models.tabelas import db, Colaborador, Ponto   # Puxando tabelas do BD para comunicação

# Definindo Blueprint
ponto_blueprint = Blueprint('ponto', __name__, template_folder='templates')

# Rota "Registrrar_Ponto"
@ponto_blueprint.route('/', methods=['GET', 'POST'])
def registrar_ponto():

    # Definindo o fuso horário considerando o de SP(UTC-3)
    tz = pytz.timezone('America/Sao_Paulo')
    agora = datetime.now(tz)                # Data hora de hoje
    hoje = agora.date()                     # Apenas a data de hoje (sem a hora)

    if request.method == 'POST':
        # Recebendo dados do formulário no html
        matricula = request.form.get('matricula')
        senha = request.form.get('senha')

        # Verifica se tem o preenchimento da matricula + senha (por mais que já seja obrigatório no html)
        if not matricula or not senha:
            flash("Matrícula e senha são obrigatórias.", "danger")
            return redirect(url_for('ponto.registrar_ponto'))

        # Puxa as informações do colaborador com base na matricula se ele estiver ativo
        colaborador = Colaborador.query.filter_by(Matricula=matricula, Ativo=True).first()

        # Validações antes de puxar os pontos
        # Não existe matricula informada ou incorreta
        if not colaborador:
            flash("Matrícula não encontrada ou colaborador inativo.", "danger")
            return redirect(url_for('ponto.registrar_ponto'))

        # Senha incorreta
        if not colaborador.check_senha(senha):
            flash("Senha incorreta.", "danger")
            return redirect(url_for('ponto.registrar_ponto'))
        
        # Se precisa mudar de senha (Nova_Senha do BD == True)
        if colaborador.Nova_Senha:
            login_user(colaborador)
            return redirect(url_for('login.nova_senha'))
        
        # Busca todos os pontos do dia (ordenados do mais recente para o mais antigo)
        pontos_do_dia = Ponto.query.filter(
            Ponto.Matricula == matricula,
            db.func.DATE(Ponto.Data_Hora) == hoje
        ).order_by(Ponto.Data_Hora.desc()).all()

        # Busca os pontos do dia atual do colaborador.
        if pontos_do_dia:
            ultimo_ponto = pontos_do_dia[0]  # O mais recente
            data_hora_ultimo = ultimo_ponto.Data_Hora

            # Força fuso horário, se necessário
            if data_hora_ultimo.tzinfo is None:
                data_hora_ultimo = tz.localize(data_hora_ultimo)

            # Calcula a diferença entre o ultimo ponto ponto e o registro atual
            diferenca_segundos = (agora - data_hora_ultimo).total_seconds()

            # Se o calculo der menor que 60 segundos, vai apagar o ultimo ponto no BD (O usuário registrou indevidamente)
            if diferenca_segundos < 60:
                db.session.delete(ultimo_ponto)
                db.session.commit()
                flash("Último ponto apagado. Tente registrar novamente em 15s.", "warning")
                return redirect(url_for('ponto.registrar_ponto'))

        # Define tipo do novo ponto a ser registrado (entrada ou saída)
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
    
    # Se for GET, apenas retorna o template
    return render_template("home.html")

# Rota para o colaborador solicitar o relatório
@ponto_blueprint.route('/relatorio_colaborador', methods=['GET', 'POST'])
def relatorio_colaborador():

    if request.method == 'POST':

        # Recebendo dados do formulário da página html
        matricula = request.form.get('matricula')
        senha = request.form.get('senha')
        data_inicio = request.form.get('data_inicio')
        data_fim = request.form.get('data_fim')

        # Verificações
        # Se faltar algum campo envia alerta
        if not matricula or not senha:
            flash("Matrícula e senha são obrigatórias.", "danger")
        else:
            
            # Se validade puxa as informações do colaborador pela matricula
            colaborador = Colaborador.query.filter_by(Matricula=matricula).first()

            # Se errar matricula ou senha envia alerta
            if not colaborador:
                flash("Colaborador não encontrado.", "danger")
            elif not colaborador.check_senha(senha):
                flash("Senha incorreta.", "danger")
            else:

                # Se validado, redireciona direto para o PDF com os parâmetros do colaborador
                pdf_url = url_for('ponto.relatorio_colaborador_pdf',
                                  matricula=matricula,
                                  senha=senha,
                                  data_inicio=data_inicio,
                                  data_fim=data_fim)
                return redirect(pdf_url)

     # Se for GET ou falhar validação, mostra o formulário
    return render_template(
        'relatorio_colaborador.html'
    )

@ponto_blueprint.route('/relatorio_colaborador/pdf')
def relatorio_colaborador_pdf():
    
    # Recebe os dados informados no formulario da URL anterior "/relatorio_colaborador"
    matricula = request.args.get('matricula')
    senha = request.args.get('senha')
    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')

    # Se tentar acessar sem as informações, envia alerta
    if not matricula or not senha:
        return "Acesso negado: matrícula e senha são obrigatórias.", 400

    # Puxa as informaçoes do colaborador no BD
    colaborador = Colaborador.query.filter_by(Matricula=matricula).first()

    if not colaborador:
        return "Colaborador não encontrado.", 404

    if not colaborador.check_senha(senha):
        return "Senha incorreta.", 403

    # Se for informada datas, filtra pontos do colaborador atraves delas e com a matricula.
    query = Ponto.query.filter(Ponto.Matricula == matricula)

    try:
        if data_inicio:
            inicio = datetime.strptime(data_inicio, '%Y-%m-%d')
            query = query.filter(Ponto.Data_Hora >= inicio)

        if data_fim:
            fim = datetime.strptime(data_fim, '%Y-%m-%d') + timedelta(days=1)
            query = query.filter(Ponto.Data_Hora < fim)

    except ValueError:
        pass  # Se der erro de data inválida, ignora o filtro

    # Executa a consulta final puxando as informaçoes
    pontos = query.order_by(Ponto.Data_Hora.desc()).all()
    nome_colaborador = colaborador.Nome
    data_atual = datetime.now()

    # Envia para a pagina pdf as informações
    html = render_template("pdf.html", 
                           pontos=pontos, 
                           matricula=matricula, 
                           nome=nome_colaborador,
                           data_atual=data_atual)

    # Converte para PDF
    pdf = HTML(string=html).write_pdf()

    return Response(pdf, mimetype='application/pdf',
                    headers={'Content-Disposition': 'inline; filename=relatorio_pontos_colaborador.pdf'})


