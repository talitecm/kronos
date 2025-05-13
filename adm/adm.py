from utilidades import *            # Importando todas bibliotecas
from models.tabelas import *        # Importando tabelas do Banco de dados 

adm_blueprint = Blueprint('adm', __name__, template_folder='templates')

def gerar_senha_temporaria(tamanho=8):
    caracteres = string.ascii_letters + string.digits
    return ''.join(random.choices(caracteres, k=tamanho))

@adm_blueprint.route('/adm')
@login_required
def adm():
    return render_template('adm.html')

@adm_blueprint.route('/adm/consultar', methods=['GET', 'POST'])
@login_required
def consultar():
    if request.method == 'POST':
        matricula = request.form.get('matricula')
        colaborador = Colaborador.query.filter_by(Matricula=matricula).first()

        if not colaborador:
            flash("Colaborador não encontrado.", "danger")
            return redirect(url_for('adm.consultar'))

        # Busca informações adicionais se for administrador
        admin = Administrador.query.filter_by(Matricula=matricula).first()

        return render_template('consultar.html', colaborador=colaborador, admin=admin)

    return render_template('consultar.html')

@adm_blueprint.route('/adm/editar/<matricula>', methods=['GET', 'POST'])
@login_required
def editar(matricula):
    from app import mail

    colaborador = Colaborador.query.filter_by(Matricula=matricula).first_or_404()
    admin = Administrador.query.filter_by(Matricula=matricula).first()

    if request.method == 'POST':
        nome = request.form.get('nome')
        administrador_selecionado = request.form.get('administrador') == '1'
        ativo = request.form.get('ativo') == '1'
        email = request.form.get('email')
        senha = gerar_senha_temporaria()

        # Atualiza dados do colaborador
        colaborador.Nome = nome
        colaborador.Ativo = ativo

        if administrador_selecionado:
            if not admin:
                # Cria novo administrador
                novo_admin = Administrador(
                    Matricula=colaborador.Matricula,
                    Email=email,
                    Senha=senha
                )
                db.session.add(novo_admin)
                msg = Message(
                    subject="Kronos - Sistema de Ponto",
                    recipients=[email],
                    body=f"Olá {novo_colaborador.Nome}, Atualizamos seu cadastro!!\n\nSua matricula é: {proxima_matricula}\nSua senha provisória: {senha}\n\nPor favor, não esqueça da sua matrícula e ao inserir sua senha pela primeira vez, altere-a para uma mais segura."
                )
                mail.send(msg)

            else:
                # Atualiza email e, se houver senha, atualiza também
                admin.Email = email
                if senha:
                    admin.Senha = senha
        else:
            if admin:
                db.session.delete(admin)

        db.session.commit()
        flash("Dados atualizados com sucesso!", "success")
        return redirect(url_for('adm.consultar', matricula=colaborador.Matricula))

    return render_template('editar.html', colaborador=colaborador, admin=admin)


@adm_blueprint.route('/adm/cadastrar')
@login_required
def cadastrar():
    ultima = Colaborador.query.order_by(Colaborador.Matricula.desc()).first()
    proxima_matricula = ultima.Matricula + 1 if ultima else 1000  # ex: começa em 1000

    return render_template('cadastrar.html', proxima_matricula=proxima_matricula)

@adm_blueprint.route('/salvar_cadastro', methods=['POST'])
@login_required

def salvar_cadastro():
    from app import mail

    nome = request.form.get('nome')
    administrador = request.form.get('administrador') == '1'
    email = request.form.get('email')
    senha = gerar_senha_temporaria()

    if not nome:
        flash("Nome completo obrigatório.", "danger")
        return redirect(url_for('adm.cadastrar'))

    # Gera a matrícula aqui, sem depender do HTML
    ultima = Colaborador.query.order_by(Colaborador.Matricula.desc()).first()
    proxima_matricula = ultima.Matricula + 1 if ultima else 1000

    try:
        novo_colaborador = Colaborador(
            Matricula=proxima_matricula,
            Nome=nome,
            Ativo=True
        )
        db.session.add(novo_colaborador)

        if administrador:
            if not email or not senha:
                flash("E-mail e senha são obrigatórios para administradores.", "danger")
                return redirect(url_for('adm.cadastrar'))

            novo_admin = Administrador(
                Matricula=proxima_matricula,
                Email=email,
                Senha=senha
            )
            db.session.add(novo_admin)

        db.session.commit()

        msg = Message(
            subject="Kronos - Sistema de Ponto",
            recipients=[email],
            body=f"Olá {novo_colaborador.Nome}, Seja bem vindo!!\n\nSua matricula é: {proxima_matricula}\nSua senha provisória: {senha}\n\nPor favor, não esqueça da sua matrícula e ao inserir sua senha pela primeira vez, altere-a para uma mais segura."
        )
        mail.send(msg)

        flash(f"Colaborador cadastrado com sucesso! Matrícula: {proxima_matricula}\n\nEnviamos um novo e-mail para o endereço {email}, informando a matricula e a senha para primeiro acesso do usuário.", "success")
        return redirect(url_for('adm.cadastrar'))
    except Exception as e:
        db.session.rollback()
        flash(f"Erro ao cadastrar colaborador: {str(e)}", "danger")
        return redirect(url_for('adm.cadastrar'))

@adm_blueprint.route('/adm/relatorio', methods=['GET', 'POST'])
@login_required
def relatorio():
    data_atual = datetime.now()  # ✅ Definida antes de tudo

    pontos = []
    matricula = ''
    nome = ''
    tipo_filtro = ''
    data_inicio = ''
    data_fim = ''
    mes = ''
    data = ''

    if request.method == 'POST':
        matricula = request.form.get('matricula')
        nome = request.form.get('nome')
        tipo_filtro = request.form.get('tipo_filtro')
        data_inicio = request.form.get('data_inicio')
        data_fim = request.form.get('data_fim')
        mes = request.form.get('mes')
        data = request.form.get('data')
        data_atual = datetime.now()

        query = Ponto.query

        if matricula:
            query = query.filter(Ponto.Matricula == matricula)

        if nome:
            query = query.join(Colaborador).filter(Colaborador.Nome.like(f"%{nome}%"))

        if tipo_filtro == 'mes' and mes:
            try:
                ano_mes = datetime.strptime(mes, '%Y-%m')
                inicio = datetime(ano_mes.year, ano_mes.month, 1)
                fim = datetime(ano_mes.year, ano_mes.month + 1, 1) if ano_mes.month < 12 else datetime(ano_mes.year + 1, 1, 1)
                query = query.filter(Ponto.Data_Hora >= inicio, Ponto.Data_Hora < fim)
            except ValueError:
                flash("Mês inválido.", "danger")

        elif tipo_filtro == 'data' and data:
            try:
                data_unico = datetime.strptime(data, '%Y-%m-%d')
                query = query.filter(db.func.DATE(Ponto.Data_Hora) == data_unico.date())
            except ValueError:
                flash("Data inválida.", "danger")

        elif tipo_filtro == 'periodo' and data_inicio and data_fim:
            try:
                inicio = datetime.strptime(data_inicio, '%Y-%m-%d')
                fim = datetime.strptime(data_fim, '%Y-%m-%d')

                if inicio > fim:
                    flash("Data inicial maior que a final.", "danger")
                else:
                    query = query.filter(Ponto.Data_Hora >= inicio, Ponto.Data_Hora <= fim)
            except ValueError:
                flash("Datas inválidas.", "danger")

        pontos = query.all()

    else:
        pontos = Ponto.query.all()

    return render_template(
        'relatorio.html',
        pontos=pontos,
        matricula=matricula,
        nome=nome,
        tipo_filtro=tipo_filtro,
        data_inicio=data_inicio,
        data_fim=data_fim,
        mes=mes,
        data=data,
        data_atual=data_atual
    )

@adm_blueprint.route('/relatorio/pdf')
@login_required
def relatorio_pdf():
    matricula = request.args.get('matricula')
    nome = request.args.get('nome')
    tipo_filtro = request.args.get('tipo_filtro')
    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')
    mes = request.args.get('mes')
    data = request.args.get('data')

    query = Ponto.query

    if matricula:
        query = query.filter(Ponto.Matricula == matricula)

    if nome:
        query = query.join(Colaborador).filter(Colaborador.Nome.like(f"%{nome}%"))

    if mes:
        try:
            ano_mes = datetime.strptime(mes, '%Y-%m')
            inicio = datetime(ano_mes.year, ano_mes.month, 1)
            fim = datetime(ano_mes.year, ano_mes.month + 1, 1) if ano_mes.month < 12 else datetime(ano_mes.year + 1, 1, 1)
            query = query.filter(Ponto.Data_Hora >= inicio, Ponto.Data_Hora < fim)
        except ValueError:
            pass

    elif data_inicio and data_fim:
        try:
            inicio = datetime.strptime(data_inicio, '%Y-%m-%d')
            fim = datetime.strptime(data_fim, '%Y-%m-%d')
            query = query.filter(Ponto.Data_Hora.between(inicio, fim))
        except ValueError:
            pass

    elif data:
        try:
            data_filtro = datetime.strptime(data, '%Y-%m-%d')
            query = query.filter(db.func.DATE(Ponto.Data_Hora) == data_filtro.date())
        except ValueError:
            pass

    pontos = query.all()

    # ✅ Adicionando data_atual aqui
    data_atual = datetime.now()

    html = render_template("pdf.html", 
                           pontos=pontos, 
                           matricula=matricula, 
                           nome=nome,
                           data_atual=data_atual)  # ✅ Incluída no contexto

    pdf = HTML(string=html).write_pdf()

    return Response(pdf, mimetype='application/pdf',
                    headers={'Content-Disposition': 'inline; filename=relatorio_pontos.pdf'})


