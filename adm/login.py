from bibliotecas import *
from models.tabelas import * # importando as tabelas do banco

login_blueprint = Blueprint('login', __name__, template_folder='templates')

# Função para carregar o usuário
@lm.user_loader
def load_user(matricula):
    return Colaborador.query.filter_by(Matricula=matricula).first()


@login_blueprint.route('/login', methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('adm.adm'))
    
    if request.method == "POST":
            matricula = request.form.get("matricula")
            senha = request.form.get("senha")

            colaborador = Colaborador.query.filter_by(Matricula=matricula).first()

            if not colaborador:
                flash("Matrícula inválida.", "danger")
                return redirect(url_for("login.login"))

            if not colaborador.check_senha(senha):
                flash("Senha incorreta.", "danger")
                return redirect(url_for("login.login"))

            # Verifica se o usuário é administrador
            if not colaborador.Administrador:
                flash("Acesso negado: você não tem permissão de administrador.", "danger")
                return redirect(url_for("login.login"))

            if colaborador.Nova_Senha:
                login_user(colaborador)
                return redirect(url_for('login.nova_senha'))  # Redireciona para troca de senha

            # Se tudo certo: login e REDIRECIONAMENTO
            login_user(colaborador)
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

        administrador = Colaborador.query.filter_by(Email=email).first()

        if not administrador:
            flash("E-mail não encontrado.", "danger")
            return redirect(url_for('login.recuperar_senha'))

        nova_senha = gerar_senha_temporaria()
        administrador.set_senha(nova_senha)
        administrador.Nova_Senha = True
        db.session.commit()

        # ✉️ Enviar e-mail com a nova senha
        msg = Message(
            subject="Recuperação de Senha - Sistema de Ponto",
            recipients=[email],
            body=f"Olá {administrador.Nome}, sua nova senha é: {nova_senha}\n\nPor favor, faça login e altere-a para uma senha segura."
        )
        mail.send(msg)

        flash("Foi enviado um e-mail com sua nova senha.", "success")
        return redirect(url_for('login.login'))

    return render_template('recuperar_senha.html')

@login_blueprint.route('/nova_senha', methods=['GET', 'POST'])
@login_required
def nova_senha():
    if request.method == 'POST':
        nova_senha = request.form.get('nova_senha')
        confirmar_nova_senha = request.form.get('confirmar_nova_senha')

        if nova_senha != confirmar_nova_senha:
            flash("As senhas não coincidem.", "danger")
            return redirect(url_for('login.nova_senha'))

        if len(nova_senha) < 4:
            flash("A senha deve ter pelo menos 4 caracteres.", "danger")
            return redirect(url_for('login.nova_senha'))

        # Atualiza senha e marca como já alterada
        current_user.set_senha(nova_senha)
        current_user.Nova_Senha = False
        db.session.commit()

        flash("Senha atualizada com sucesso!", "success")
        return redirect(url_for('ponto.registrar_ponto'))

    return render_template('nova_senha.html')