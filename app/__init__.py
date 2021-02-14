from flask import Flask, request
from config import Config
from dotenv import load_dotenv
from flask_bootstrap import Bootstrap
from datetime import datetime
from flask_babelex import Babel
from flask_sqlalchemy import SQLAlchemy

# Load .env file
load_dotenv()

# Initialize flask app
app = Flask(__name__)
app.config.from_object(Config)

# Initialize Bootstrap tamplate
Bootstrap(app)

# Initialize Babel translation
babel = Babel(app)

# Initialize SQLAlchemy database connector
db = SQLAlchemy(app)

# Add Date filter for jinja2 views
def parse_stringDates_formats(value, format1="%Y-%m-%d", format2="%d/%m"):
    return datetime.strptime(value,format1).strftime(format2) if value != "" else ""

app.jinja_env.filters['parse_stringDates_formats'] = parse_stringDates_formats

# Add language selection
@babel.localeselector
def get_locale():
    if request.args.get('lang'):
        return request.args.get('lang')
    return request.accept_languages.best_match(app.config['LANGUAGES'])

# Import app components
from app import routes
from app import cli
from app.models import *
from app import admin
