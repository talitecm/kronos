from bibliotecas import *           # Importando todas bibliotecas
from models.tabelas import *        # Importando tabelas do Banco de dados 

# Cria um Blueprint para as rotas administrativas
adm_blueprint = Blueprint('adm', __name__, template_folder='templates')

# Função para gerar senha temporária
def gerar_senha_temporaria(tamanho=8):
    caracteres = string.ascii_letters + string.digits
    return ''.join(random.choices(caracteres, k=tamanho))

# Rota Inicial do ADm
@adm_blueprint.route('/adm')
@login_required
def adm():
    if not current_user.Administrador:
        flash("Você não tem permissão para acessar esta página.", "danger")
        return redirect(url_for('login.logout'))
        
    return render_template('adm.html')

# Rota para consultar colaborador
@adm_blueprint.route('/adm/consultar', methods=['GET', 'POST'])
@login_required
def consultar():
    if request.method == 'POST':
        matricula = request.form.get('matricula')
        colaborador = Colaborador.query.filter_by(Matricula=matricula).first()

        if not colaborador:
            flash("Colaborador não encontrado.", "danger")
            return redirect(url_for('adm.consultar'))

        return render_template('consultar.html', colaborador=colaborador)

    return render_template('consultar.html')

# Rota para editar colaborador consultado
@adm_blueprint.route('/adm/editar/<matricula>', methods=['GET', 'POST'])
@login_required
def editar(matricula):

    colaborador = Colaborador.query.filter_by(Matricula=matricula).first_or_404()

    if request.method == 'POST':
        nome = request.form.get('nome')
        administrador = request.form.get('administrador') == '1'
        ativo = request.form.get('ativo') == '1'
        email = request.form.get('email')
        senha = gerar_senha_temporaria()

        # Atualiza dados do colaborador
        colaborador.Nome = nome
        colaborador.Ativo = ativo
        colaborador.Email = email
        colaborador.Administrador = administrador

        db.session.commit()
        flash("Dados atualizados com sucesso!", "success")
        return redirect(url_for('adm.consultar', matricula=colaborador.Matricula))

    return render_template('editar.html', colaborador=colaborador)

# Rota para cadastrar novo colaborador
@adm_blueprint.route('/adm/cadastrar')
@login_required
def cadastrar():
    ultima = Colaborador.query.order_by(Colaborador.Matricula.desc()).first()
    proxima_matricula = ultima.Matricula + 1 if ultima else 1000  # Variável para mostrar a proxima matricula (soma + 1 com base na ultima matricula)

    return render_template('cadastrar.html', proxima_matricula=proxima_matricula)

# Rota para salvar os dados cadastrados
@adm_blueprint.route('/salvar_cadastro', methods=['POST'])
@login_required

def salvar_cadastro():
    from app import mail

    nome = request.form.get('nome')
    administrador = request.form.get('administrador') == '1'
    email = request.form.get('email')

    # Verifica se já existe colaborador com esse e-mail
    if Colaborador.query.filter_by(Email=email).first():
        flash("Este e-mail já está cadastrado.", "danger")
        return redirect(url_for('adm.cadastrar'))

    # 
    if not nome or not email:
        flash("Dados obrigatórios.", "danger")
        return redirect(url_for('adm.cadastrar'))

    # Gera a matrícula
    ultima = Colaborador.query.order_by(Colaborador.Matricula.desc()).first()
    proxima_matricula = ultima.Matricula + 1 if ultima else 1000

    try:
        senha = gerar_senha_temporaria() # Cria uma senha aleatória

        novo_colaborador = Colaborador(
            Matricula=proxima_matricula,
            Nome=nome,
            Email=email,
            Administrador=administrador,
            Ativo=True,
            Nova_Senha=True, # Para que ele precise registar nova senha no próximo registro (login ou ponto)
        )
        novo_colaborador.set_senha(senha) # Cria o hash criptografando a senha antes de salvar

        db.session.add(novo_colaborador)
        db.session.commit()

        msg = Message(
            subject="Kronos - Sistema de Ponto",
            recipients=[email],
            body=f"Olá {novo_colaborador.Nome}, Seja bem vindo(a)!!\n\nSua matricula é: {proxima_matricula}\nSua senha provisória: {senha}\n\nhttps://kronos-gestao-do-tempo.onrender.com\n\nPor favor, não esqueça da sua matrícula e ao inserir sua senha pela primeira vez, altere-a para uma mais segura."
        )

        mail.send(msg)
        flash(f"Colaborador cadastrado com sucesso! Enviamos um novo e-mail para o endereço {email} informando a matricula e a senha para primeiro acesso do usuário.", "success")
        return redirect(url_for('adm.cadastrar'))
    except Exception as e:
        db.session.rollback()
        flash(f"Erro ao cadastrar colaborador: {str(e)}", "danger")
        return redirect(url_for('adm.cadastrar'))

# Rota relatório
@adm_blueprint.route('/adm/relatorio', methods=['GET', 'POST'])
@login_required
def relatorio():

    # Puxando os pontos do mês atual
    pontos = []
    matricula = ''
    nome = ''
    data_inicio = request.form.get('data_inicio') if request.method == 'POST' else None
    data_fim = request.form.get('data_fim') if request.method == 'POST' else None

    hoje = datetime.now()
    
    # Define datas padrão: início e fim do mês atual
    if not data_inicio and not data_fim and request.method == 'GET':
        inicio_mes = hoje.replace(day=1)
        fim_mes = (inicio_mes + timedelta(days=32)).replace(day=1) - timedelta(days=1)

        data_inicio = inicio_mes.strftime('%Y-%m-%d')
        data_fim = fim_mes.strftime('%Y-%m-%d')

    query = Ponto.query

    if request.method == 'POST':
        matricula = request.form.get('matricula')
        nome = request.form.get('nome')

        if matricula:
            query = query.filter(Ponto.Matricula == matricula)

        if nome:
            query = query.join(Colaborador).filter(Colaborador.Nome.like(f"%{nome}%"))

    try:
        inicio = None
        fim = None

        if data_inicio:
            inicio = datetime.strptime(data_inicio, '%Y-%m-%d')
            query = query.filter(Ponto.Data_Hora >= inicio)

        if data_fim:
            fim = datetime.strptime(data_fim, '%Y-%m-%d') + timedelta(days=1)
            query = query.filter(Ponto.Data_Hora < fim)

    except ValueError:
        flash("Datas inválidas.", "danger")

    pontos = query.order_by(Ponto.Data_Hora.desc()).all()

    return render_template(
        'relatorio.html',
        pontos=pontos,
        matricula=matricula,
        nome=nome,
        data_inicio=data_inicio,
        data_fim=data_fim
    )

# Rota pdf puxando os dados do formulario anterior
@adm_blueprint.route('/relatorio/pdf')
@login_required
def relatorio_pdf():
    matricula = request.args.get('matricula')
    nome = request.args.get('nome')
    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')

    query = Ponto.query

    if matricula:
        query = query.filter(Ponto.Matricula == matricula)

    if nome:
        query = query.join(Colaborador).filter(Colaborador.Nome.like(f"%{nome}%"))
    
    try:
        inicio = None
        fim = None

        if data_inicio:
            inicio = datetime.strptime(data_inicio, '%Y-%m-%d')
            query = query.filter(Ponto.Data_Hora >= inicio)

        if data_fim:
            fim = datetime.strptime(data_fim, '%Y-%m-%d') + timedelta(days=1)
            query = query.filter(Ponto.Data_Hora < fim)

    except ValueError:
        pass 
    
    # Puxa os pontos registrados
    pontos = query.order_by(Ponto.Data_Hora.desc()).all()

    # Busca o nome do colaborador, se houver matrícula
    nome_colaborador = None
    if matricula:
        colaborador = Colaborador.query.filter_by(Matricula=matricula).first()
        if colaborador:
            nome_colaborador = colaborador.Nome

    data_atual = datetime.now()

    # Gera o HTML para o PDF
    html = render_template("pdf.html", 
                           pontos=pontos, 
                           matricula=matricula, 
                           nome=nome_colaborador or nome,
                           data_atual=data_atual)

    # Converte para PDF
    pdf = HTML(string=html,  base_url=request.url_root).write_pdf()
    
    return Response(pdf, mimetype='application/pdf',
                    headers={'Content-Disposition': 'inline; filename=relatorio_pontos.pdf'})

