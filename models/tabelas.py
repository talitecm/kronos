from bibliotecas import *

class Colaborador(db.Model, UserMixin):
    __tablename__ = 'colaborador'

    Matricula = db.Column(db.Integer, primary_key=True)
    Nome = db.Column(db.String(100))
    Administrador = db.Column(db.Boolean, default=False)  # Indica se é admin
    Ativo = db.Column(db.Boolean, default=True)
    Senha = db.Column(db.String(600))               # Armazena hash da senha
    Nova_Senha = db.Column(db.Boolean, default=True)  # Para redefinição de senha
    Email = db.Column(db.String(100))

    def set_senha(self, senha):
        self.Senha = generate_password_hash(senha)

    def check_senha(self, senha):
        return check_password_hash(self.Senha, senha)

    def get_id(self):
        return str(self.Matricula)  # Retorna a matrícula como ID do usuário

    @property
    def is_active(self):
        return self.Ativo  # Retorna True/False se o colaborador estiver ativo

    # Relacionamento com a tabela Ponto
    pontos = db.relationship('Ponto', backref='colaborador', lazy=True)

class Ponto(db.Model):
    __tablename__ = 'ponto'

    Id_ponto = db.Column(db.Integer, primary_key=True)
    Data_Hora = db.Column(db.DateTime, default=db.func.current_timestamp())
    Tipo = db.Column(db.String(1), nullable=True)  # '1' para entrada, '0' para saída
    Matricula = db.Column(db.Integer, db.ForeignKey('colaborador.Matricula'), nullable=False)