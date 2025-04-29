from flask_login import UserMixin
from utilidades import *

class Colaborador(db.Model, UserMixin):
    __tablename__ = 'colaborador'

    Matricula = db.Column(db.Integer, unique=True, nullable=False, primary_key=True)
    Nome = db.Column(db.String(50), nullable=False)
    CPF = db.Column(db.BigInteger, unique=True, nullable=False)
    Data_Nascimento = db.Column(db.Date, nullable=False)
    Email = db.Column(db.String(80), unique=True, nullable=False)
    Admissao = db.Column(db.Date, nullable=False)
    Administrador = db.Column(db.Boolean, nullable=False)

    Senha = db.Column(db.String(8), nullable=False)
    Ativo = db.Column(db.Boolean)

    def __repr__(self):
        return f"<Colaborador {self.Matricula}>"
    
    def get_id(self):
        return str(self.Matricula)  # Retorna a matrícula como ID do usuário

    @property
    def is_active(self):
        return self.Ativo  # Retorna True/False se o colaborador estiver ativo