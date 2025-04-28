from flask import Flask, render_template, request, redirect, url_for, flash                     # Importando Flask
from utilidades import *                                                                        # Importando banco de dados.
from models.tabelas import *                                                                    # importando a classe 
import os                                                                                       # Biblioteca para ler arquivos como se fosse um "Sistema Operacional"
from dotenv import load_dotenv                                                                  # Biblioteca para trabalhar com arquivos env
from flask_login import LoginManager, login_user, login_required, logout_user, current_user     # Biblioteca para gerenciar sessões de Login
from datetime import datetime                                                                   # Importando uma forma de pegar a data/hora atual
import pytz                                                                                     # Biblioteca para lidar com fusos horários.
from rota_adm.adm import adm_blueprint                                                          # Importando o blueprint para rotas de adm.
from rota_colaborador.colaborador import colaborador_blueprint                                  # Importando o blueprint para rotas de colaborador.

app = Flask(__name__)

app.register_blueprint(adm_blueprint)                                                           # Registrando rota adm.
app.register_blueprint(colaborador_blueprint)                                                   # Registrando rota colaborador.

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


# Função para carregar o usuário
@lm.user_loader
def load_user(matricula):
    return Pessoa.query.filter_by(Matricula=matricula).first()                                  # Busca o usuário no banco pela matricula // em caso de incompatibilidades Verififcar "Pessoa"