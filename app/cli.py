from app import app
from app import db
from app.models import *
from werkzeug.security import generate_password_hash
import click
import os

@app.cli.group()
def migrate():
    """Database migrations commands."""
    pass

@migrate.command()
def up():
    """Create database"""
    db.create_all()

@migrate.command()
def down():
    """Drop database"""
    db.drop_all()

@migrate.command()
def refresh():
    """Runs down then up"""
    db.drop_all()
    db.create_all()
    newUser = User(email='root@root.net', password=generate_password_hash('root'))
    db.session.add(newUser)
    db.session.commit()

@app.cli.group()
def adminuser():
    """Admin user commands."""
    pass

@adminuser.command()
@click.argument('email')
@click.argument('password')
def create(email, password):
    newUser = User(email=email, password=generate_password_hash(password))
    db.session.add(newUser)
    db.session.commit()
    return

@app.cli.group()
def translate():
    """Translation and localization commands."""
    pass

@translate.command()
def update():
    """Update all languages."""
    if os.system('pybabel extract -F babel.cfg -k _l -o messages.pot .'):
        raise RuntimeError('extract command failed')
    if os.system('pybabel update -i messages.pot -d app/translations'):
        raise RuntimeError('update command failed')
    os.remove('messages.pot')

@translate.command()
def compile():
    """Compile all languages."""
    if os.system('pybabel compile -d app/translations'):
        raise RuntimeError('compile command failed')

@translate.command()
@click.argument('lang')
def init(lang):
    """Initialize a new language."""
    if os.system('pybabel extract -F babel.cfg -k _l -o messages.pot .'):
        raise RuntimeError('extract command failed')
    if os.system('pybabel init -i messages.pot -d app/translations -l ' + lang):
        raise RuntimeError('init command failed')
    os.remove('messages.pot')