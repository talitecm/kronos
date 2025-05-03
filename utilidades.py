from flask_sqlalchemy import SQLAlchemy
from flask import Flask, Blueprint, render_template, request, redirect, url_for, flash          # Importando Flask
import os                                                                                       # Biblioteca para ler arquivos como se fosse um "Sistema Operacional"
from dotenv import load_dotenv                                                                  # Biblioteca para trabalhar com arquivos env
from flask_login import LoginManager, login_user, login_required, logout_user, current_user     # Biblioteca para gerenciar sessões de Login
from datetime import datetime, date                                                             # Importando uma forma de pegar a data/hora atual
import pytz                                                                                     # Biblioteca para lidar com fusos horários.
import mysql.connector

db = SQLAlchemy()
lm = LoginManager()