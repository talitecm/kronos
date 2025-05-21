from bibliotecas import * # Importando bibliotecas necessárias

# Classe Colaborador comunicando com a tabela "colaborador" do BD
class Colaborador(db.Model, UserMixin):
    __tablename__ = 'colaborador'                           # Nome da tabela no banco de dados

    # Campos principais do colaborador
    Matricula = db.Column(db.Integer, primary_key=True)     # ID único do colaborador
    Nome = db.Column(db.String(100))                        # Nome do colaborador
    Email = db.Column(db.String(100))                       # E-mail
    Senha = db.Column(db.String(600))                       # Armazena hash da senha
    Ativo = db.Column(db.Boolean, default=True)             # Indica se o colaborador está ativo
    Nova_Senha = db.Column(db.Boolean, default=True)        # Para redefinição de senha
    Administrador = db.Column(db.Boolean, default=False)    # Indica se é admin ou não
    
    # Gera um hash seguro para a senha e armazena
    def set_senha(self, senha):
        self.Senha = generate_password_hash(senha)
    
    # Verifica se a senha informada é correspondente ao hash salvo
    def check_senha(self, senha):
        return check_password_hash(self.Senha, senha)

    # Retorna a matricula como ID do usuário
    def get_id(self):
        return str(self.Matricula) 

    # Define se o colaborador pode fazer login 
    @property
    def is_active(self):
        return self.Ativo  # Retorna True/False se o colaborador estiver ativo

    # Relacionamento com a tabela Ponto
    pontos = db.relationship('Ponto', backref='colaborador', lazy=True)

# Classe Ponto comunicando com a tabela "ponto" do BD
class Ponto(db.Model):
    __tablename__ = 'ponto'                                                                     # Nome da tabela no banco de dados

    Id_ponto = db.Column(db.Integer, primary_key=True)                                          # Identificador único do registro
    Data_Hora = db.Column(db.DateTime, default=db.func.current_timestamp())                     # Data-hora do registro
    Tipo = db.Column(db.String(1), nullable=True)                                               # '1' para entrada, '0' para saída
    Matricula = db.Column(db.Integer, db.ForeignKey('colaborador.Matricula'), nullable=False)   # Matricula da tabela colaborador