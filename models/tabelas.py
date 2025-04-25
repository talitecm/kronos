from flask_login import UserMixin
from utilidades import *
from flask_sqlalchemy import SQLAlchemy

class Pessoa(db.Model):
    __tablename__ = 'pessoa'

    idPessoa = db.Column(db.Integer, primary_key=True)
    Nome = db.Column(db.String(50), nullable=False)
    CPF = db.Column(db.BigInteger, unique=True, nullable=False)
    Data_Nascimento = db.Column(db.Date, nullable=False)
    Email = db.Column(db.String(80), unique=True, nullable=False)
    Admissao = db.Column(db.Date, nullable=False)
    Administrador = db.Column(db.Boolean, nullable=False)
    Matricula = db.Column(db.Integer, unique=True, nullable=False)
    Senha = db.Column(db.String(8), nullable=False)
    Ativo = db.Column(db.Boolean, nullable=False)

    enderecos = db.relationship('EnderecoPessoa', back_populates='pessoa', cascade='all, delete-orphan')
    contatos = db.relationship('ContatoPessoa', back_populates='pessoa', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Pessoa {self.idPessoa} - {self.Nome}>"