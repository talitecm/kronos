from flask import *
from bibliotecas import *
from adm.adm import adm_blueprint                                                           # Importando o blueprint para rotas de adm.
from ponto.ponto import ponto_blueprint                                                     # Importando o blueprint para rotas de ponto.
from adm.login import login_blueprint

app = Flask(__name__)

app.register_blueprint(adm_blueprint)                                                           # Registrando rota adm.
app.register_blueprint(ponto_blueprint)   
app.register_blueprint(login_blueprint)                                                         # Registrando rota colaborador.

app.config.from_mapping({
    'MAIL_SERVER': 'smtp.gmail.com',
    'MAIL_PORT': 587,
    'MAIL_USE_TLS': True,
    'MAIL_USERNAME': 'kronos.sistema@gmail.com',
    'MAIL_PASSWORD': 'waux rhgh htqf morq',
    'MAIL_DEFAULT_SENDER': 'kronos.sistema@gmail.com'
})

mail = Mail(app)

load_dotenv()                                                                                   # Carrega variáveis do nosso arquivo .flaskenv

dbusuario = os.getenv("DB_USERNAME")                                                            # Importando informação de usuário do arquivo env
dbsenha = os.getenv("DB_PASSWORD")                                                              # Importando informação de senha do arquivo env
host = os.getenv("DB_HOST")                                                                     # Importando informação de host do arquivo env
meubanco = os.getenv("DB_DATABASE")                                                             # Importando informação de banco de dados do arquivo env
porta = os.getenv("DB_PORT", "3306")                                                                    # importando a informação da porta da conexão do arquivo env
conexao = f"mysql+pymysql://{dbusuario}:{dbsenha}@{host}:{porta}/{meubanco}"                    # Formatando a linha de conexão com o banco
app.config["SQLALCHEMY_DATABASE_URI"] = conexao                                                 # Criando uma "rota" de comunicação
db.init_app(app)                                                                                # Sinaliza que o banco será gerenciado pelo app
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')                                              # Importando a secret key do flaskenv
lm.init_app(app)                                                                                # Sinalizando que o loginManager será gerenciado pelo app

# Erro de solicitação inválida
@app.errorhandler(400)
def bad_request(e):
    return render_template("error.html", erro="Solicitação Inválida", mensagem="Solicitação inválida. Dados ausentes ou incorretos."), 400

# Erro de página não encontrada
@app.errorhandler(404)
def pagina_nao_encontrada(e):
    return render_template("error.html", erro="Página não encontrada", mensagem="Solicitação inválida. Dados ausentes ou incorretos."), 404

# Erro de método Não Permitido
@app.errorhandler(405)
def method_not_allowed(e):
    return render_template("error.html", erro="Método Não Permitido", mensagem="Método não permitido para esta página."), 405

# Erro Interno no Servidor
@app.errorhandler(500)
def internal_server_error(e):
    return render_template("error.html",  erro="Erro Interno no Servidor", mensagem="Erro interno no servidor. Tente novamente mais tarde."), 500

# Aviso de acesso não autorizado
lm.login_view = 'login.login'
lm.login_message = 'Acesso restrito. Faça login primeiro.'
lm.login_message_category = 'danger'
lm.remember_cookie_duration = timedelta(minutes=1)
