import os
from decimal import Decimal, InvalidOperation
from datetime import datetime, date
import random
from flask import Flask, send_file, session, redirect, url_for, render_template, request, flash, jsonify,make_response
from flask_mail import Mail, Message
from werkzeug.security import check_password_hash, generate_password_hash
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from flask_session import Session
from sqlalchemy import create_engine, text, not_, and_, func, select
from sqlalchemy.orm import *
from sqlalchemy.orm import joinedload
from flask_sqlalchemy import SQLAlchemy
from model import *
import requests

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SESSION_PERMANENT"] = False
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'ingsoftwar123@gmail.com'
app.config['MAIL_PASSWORD'] = 'xishvjfvtnrabdpj'
app.secret_key = 'tu_clave_secreta'
mail = Mail(app)

engine = create_engine(os.getenv("DATABASE_URL"))
db_session = scoped_session(sessionmaker(bind=engine))