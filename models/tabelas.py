from utilidades import *

class Colaborador(db.Model, UserMixin):
    __tablename__ = 'colaborador'

    Matricula = db.Column(db.Integer, unique=True, nullable=False, primary_key=True)
    Nome = db.Column(db.String(50), nullable=False)
    Ativo = db.Column(db.Boolean)

    def get_id(self):
        return str(self.Matricula)  # Retorna a matrícula como ID do usuário

    @property
    def is_active(self):
        return self.Ativo  # Retorna True/False se o colaborador estiver ativo

    # Relacionamento com a tabela Ponto
    pontos = db.relationship('Ponto', backref='colaborador', lazy=True)

class Administrador(db.Model, UserMixin):
    __tablename__ = 'administrador'

    Matricula = db.Column(db.Integer, unique=True, nullable=False, primary_key=True)
    Idadministrador = db.Column(db.String(50), nullable=False)
    Email = db.Column(db.String(80), unique=True, nullable=False)
    Senha = db.Column(db.String(8), nullable=False)


    def __repr__(self):
        return f"<administrador {self.Matricula}>"
    
    def get_id(self):
        return str(self.Matricula)  # Retorna a matrícula como ID do usuário



class Ponto(db.Model):
    __tablename__ = 'ponto'

    Id_ponto = db.Column(db.Integer, primary_key=True)
    Data_Hora = db.Column(db.DateTime, default=db.func.current_timestamp())
    Tipo = db.Column(db.String(1), nullable=True)  # '1' para entrada, '0' para saída
    Matricula = db.Column(db.Integer, db.ForeignKey('colaborador.Matricula'), nullable=False)