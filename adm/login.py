from utilidades import *
from models.tabelas import * # importando as tabelas do banco

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
    logout_user()                                         # Desloga o usuário da sessão
    return redirect(url_for('ponto.registrar_ponto'))     # Redireciona para a tela de login

def gerar_senha_temporaria(tamanho=8):
    caracteres = string.ascii_letters + string.digits
    return ''.join(random.choices(caracteres, k=tamanho))

@login_blueprint.route('/recuperar_senha', methods=['GET', 'POST'])
def recuperar_senha():
    from app import mail
    
    if request.method == 'POST':
        email = request.form.get('email')

        admin = Administrador.query.filter_by(Email=email).first()

        if not admin:
            flash("E-mail não encontrado.", "danger")
            return redirect(url_for('login.recuperar_senha'))

        nova_senha = gerar_senha_temporaria()
        admin.Senha = nova_senha
        db.session.commit()

        # ✉️ Enviar e-mail com a nova senha
        msg = Message(
            subject="Recuperação de Senha - Sistema de Ponto",
            recipients=[email],
            body=f"Olá {admin.colaborador.Nome}, sua nova senha é: {nova_senha}\n\nPor favor, faça login e altere-a para uma senha segura."
        )
        mail.send(msg)

        flash("Foi enviado um e-mail com sua nova senha.", "success")
        return redirect(url_for('login.login'))

    return render_template('recuperar_senha.html')
