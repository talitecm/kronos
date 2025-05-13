from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from flask import Flask, Blueprint, render_template, request, redirect, url_for, flash, jsonify, Response, current_app  # Importando Flask
import os, pytz, mysql.connector, logging, random, string                                                               # Biblioteca para ler arquivos como se fosse um "Sistema Operacional"
from dotenv import load_dotenv                                                                                          # Biblioteca para trabalhar com arquivos env
from flask_login import UserMixin, LoginManager, login_user, login_required, logout_user, current_user                  # Biblioteca para gerenciar sessões de Login
from datetime import datetime, date                                                                                     # Importando uma forma de pegar a data/hora atual
from weasyprint import HTML
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()
lm = LoginManager()