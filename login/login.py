from bibliotecas import *           # Importando bibliotecas necessárias
from models.tabelas import *        # importando as tabelas do banco

# Definindo blueprint para Login
login_blueprint = Blueprint('login', __name__, template_folder='templates')

# Função para carregar o usuário
@lm.user_loader
def load_user(matricula):
    return Colaborador.query.filter_by(Matricula=matricula).first()

# Rota login
@login_blueprint.route('/login', methods=["GET", "POST"])
def login():

    # Se já estiver logado, redireciona direto para o painel administrativo
    if current_user.is_authenticated:
        return redirect(url_for('adm.adm'))
    
    if request.method == "POST":
            matricula = request.form.get("matricula")
            senha = request.form.get("senha")

            # Busca colaborador pelo número da matrícula
            colaborador = Colaborador.query.filter_by(Matricula=matricula).first()

            #Vefificações
            # Se não encontrar no BD Envia alerta
            if not colaborador:
                flash("Matrícula inválida.", "danger")
                return redirect(url_for("login.login"))

            # Se a senha estiver incorreta
            if not colaborador.check_senha(senha):
                flash("Senha incorreta.", "danger")
                return redirect(url_for("login.login"))

            # Verifica se o usuário é administrador
            if not colaborador.Administrador:
                flash("Acesso negado: você não tem permissão de administrador.", "danger")
                return redirect(url_for("login.login"))
            
            # Se o colaborador precisa mudar a senha (novo usuário / senha recuperada)
            if colaborador.Nova_Senha:
                login_user(colaborador)
                return redirect(url_for('login.nova_senha'))  # Redireciona para troca de senha

            # Se tudo certo: login e redireciona para a pagina de adm
            login_user(colaborador)
            return redirect(url_for("adm.adm"))

    return render_template('login.html')

# Rota de logout
@login_blueprint.route('/logout')
@login_required
def logout():
    logout_user()                                         # Desloga o usuário da sessão
    return redirect(url_for('ponto.registrar_ponto'))     # Redireciona para a tela de login

# Gera senha aleatória quando a função for chamada
def gerar_senha_temporaria(tamanho=8):
    caracteres = string.ascii_letters + string.digits
    return ''.join(random.choices(caracteres, k=tamanho))

# Rota para recuperar senha
@login_blueprint.route('/recuperar_senha', methods=['GET', 'POST'])
def recuperar_senha():
    from app import mail # Importando a biblioteca aqui para não filtrar em lugares errados.
    
    # puxa as informações do formulário do html
    if request.method == 'POST':
        matricula = request.form.get('matricula')
        email = request.form.get('email')

        # Puxa as informações do colaborador
        colaborador = Colaborador.query.filter_by(Matricula=matricula).first()


        # Verificações
        # Não existe colaborador no BD
        if not colaborador:
            flash("Matrícula inválida.", "danger")
            return redirect(url_for("login.login"))

        # O e-mail do colaborador é diferente do informado no formulário
        if colaborador.Email != email:
            flash("O e-mail informado não corresponde ao colaborador.", "danger")
            return redirect(url_for('login.recuperar_senha'))

        # Registra no BD as informações
        nova_senha = gerar_senha_temporaria() # Aqui puxa a função declarada para gerar senha aleatória
        colaborador.set_senha(nova_senha)
        colaborador.Nova_Senha = True
        db.session.commit()


        # Envia e-mail com a nova senha aleatória
        msg = Message(
            subject="Recuperação de Senha - Sistema de Ponto",
            recipients=[email],
            body=f"Olá {colaborador.Nome}, sua nova senha é: {nova_senha}\n\nPor favor, faça login e altere-a para uma senha segura."
        )
        mail.send(msg)

        flash("Foi enviado um e-mail com sua nova senha.", "success")
        return redirect(url_for('login.recuperar_senha'))

    return render_template('recuperar_senha.html')

# Rota Nova Senha, forçando o colaborador definir uma nova senha se a que foi registrada for a "temporária"
@login_blueprint.route('/nova_senha', methods=['GET', 'POST'])
@login_required
def nova_senha():
    if request.method == 'POST':
        nova_senha = request.form.get('nova_senha')
        confirmar_nova_senha = request.form.get('confirmar_nova_senha')

        # Verifica se a senhas são iguais
        if nova_senha != confirmar_nova_senha:
            flash("As senhas não coincidem.", "danger")
            return redirect(url_for('login.nova_senha'))

        # Verifica se a senha é menor que 4 digitos
        if len(nova_senha) < 4:
            flash("A senha deve ter pelo menos 4 caracteres.", "danger")
            return redirect(url_for('login.nova_senha'))

        # Atualiza senha e marca como já alterada
        current_user.set_senha(nova_senha)
        current_user.Nova_Senha = False # Faz com que não redirecione mais para a aba de nova senha
        db.session.commit()

        flash("Senha atualizada com sucesso!", "success")
        return render_template('home.html')

    return render_template('nova_senha.html')