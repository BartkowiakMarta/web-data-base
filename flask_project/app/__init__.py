from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__, static_url_path='/static')
app_dir = os.path.dirname(os.path.abspath(__file__))
app.config['UPLOAD_FOLDER'] = os.path.join(app_dir, 'files')
app.config['SQLALCHEMY_DATABASE_URI'] = r"sqlite:///project.db"
app.config['SECRET_KEY'] = 'f9ea2d5d8e333d80b2fa7a9d3f9428b3'
db = SQLAlchemy(app)

from app import routes