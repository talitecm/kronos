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

# Rota para Recuperar senha
@login_blueprint.route('/recuperar_senha')
def recuperar_senha():
    return render_template('recuperar_senha.html')