from flask import *
from utilidades import *
from adm.adm import adm_blueprint                                                           # Importando o blueprint para rotas de adm.
from ponto.ponto import ponto_blueprint                                                     # Importando o blueprint para rotas de colaborador.
from adm.login import login_blueprint


app = Flask(__name__)

app.register_blueprint(adm_blueprint)                                                           # Registrando rota adm.
app.register_blueprint(ponto_blueprint)   
app.register_blueprint(login_blueprint)                                                   # Registrando rota colaborador.

load_dotenv()                                                                                   # Carrega variáveis do nosso arquivo .flaskenv

dbusuario = os.getenv("DB_USERNAME")                                                            # Importando informação de usuário do arquivo env
dbsenha = os.getenv("DB_PASSWORD")                                                              # Importando informação de senha do arquivo env
host = os.getenv("DB_HOST")                                                                     # Importando informação de host do arquivo env
meubanco = os.getenv("DB_DATABASE")                                                             # Importando informação de banco de dados do arquivo env
porta = os.getenv("DB_PORT")                                                                    # importando a informação da porta da conexão do arquivo env
conexao = f"mysql+pymysql://{dbusuario}:{dbsenha}@{host}:{porta}/{meubanco}"                    # Formatando a linha de conexão com o banco
app.config["SQLALCHEMY_DATABASE_URI"] = conexao                                                 # Criando uma "rota" de comunicação
db.init_app(app)                                                                                # Sinaliza que o banco será gerenciado pelo app
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')                                              # Importando a secret key do flaskenv
lm.init_app(app)                                                                                # Sinalizando que o loginManager será gerenciado pelo app
