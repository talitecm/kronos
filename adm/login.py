from utilidades import *
from models.tabelas import * # importando a classe 

login_blueprint = Blueprint('login', __name__, template_folder='templates')

# Função para carregar o usuário
@lm.user_loader
def load_user(matricula):
    return Administrador.query.filter_by(Matricula=matricula).first()

@login_blueprint.route('/login', methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('adm.adm'))
    
    if request.method == "POST":
            matricula = request.form.get("matricula")
            senha = request.form.get("senha")

            usuario = Administrador.query.filter_by(Matricula=matricula).first()

            if not usuario:
                flash("Matrícula inválida.", "danger")
                return redirect(url_for("login.login"))

            if usuario.Senha != senha:
                flash("Senha incorreta.", "danger")
                return redirect(url_for("login.login"))

            # Se tudo certo: login e REDIRECIONAMENTO
            login_user(usuario)
            return redirect(url_for("adm.adm"))

    return render_template('login.html')

# Rota de logout
@login_blueprint.route('/logout')
@login_required
def logout():
    logout_user()                               # Desloga o usuário da sessão
    return redirect(url_for('login.login'))     # Redireciona para a tela de login

@login_blueprint.route('/recuperar_senha', methods=['GET', 'POST'])
def recuperar_senha():
    if request.method == 'POST':
        email = request.form.get('email')

        # Busca administrador pelo e-mail
        admin = Administrador.query.filter_by(Email=email).first()

        if not admin:
            flash("E-mail não encontrado.", "danger")
            return redirect(url_for('login.recuperar_senha'))

        # Gera nova senha temporária
        nova_senha = gerar_senha_temporaria()
        admin.Senha = nova_senha  # Atualiza a senha no banco
        db.session.commit()

        # Mensagem de sucesso
        flash(f"Sua nova senha é: {nova_senha} (válida por 5 minutos)", "success")
        return redirect(url_for('login.login'))

    return render_template('recuperar_senha.html')

# Função auxiliar para gerar senhas temporárias
def gerar_senha_temporaria(tamanho=8):
    caracteres = string.ascii_letters + string.digits
    return ''.join(random.choices(caracteres, k=tamanho))