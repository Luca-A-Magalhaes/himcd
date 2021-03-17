from app import app
from app import db
from app.models import *
from werkzeug.security import generate_password_hash
import pandas as pd
import click
import os
import math

@app.cli.group()
def data():
    """Data manipulation commands. """
    pass

@data.command()
@click.argument('file')
@click.option('--override', default=False, is_flag=True)
def load(file, override):
    try:
        df = pd.read_csv(file)
    except IOError as e:
        print(f"ERROR: Unable to read file {file}")
        exit(1)

    if override:
        CountryStatus.query.delete()
        Country.query.delete()

    for (index,row) in df.iterrows():

        country = Country.query.filter_by(name=row["Name"]).first()
        if country is None:
            country = Country(name=row["Name"])
            country.save()

        status = CountryStatus()
        status.country_id = country.id
        status.date = row["Date"] if "Date" in row else None
        status.total = row["Total"] if "Total" in row and not math.isnan(row["Total"]) else None
        status.day = row["Day"] if "Day" in row else None
        status.total_deaths = row["TotalDeaths"] if "TotalDeaths" in row and not math.isnan(row["TotalDeaths"]) else None
        status.daily_deaths = row["DailyDeaths"] if "DailyDeaths" in row and not math.isnan(row["DailyDeaths"])  else None
        status.daily_cases = row["DailyCases"] if "DailyCases" in row and not math.isnan(row["DailyCases"])  else None
        status.total_per_100k = row["TotalPer100k"] if "TotalPer100k" in row and not math.isnan(row["TotalPer100k"])  else None
        status.total_deaths_per_100k = row["TotalDeathsPer100k"] if "TotalDeathsPer100k" in row and not math.isnan(row["TotalDeathsPer100k"])  else None
        status.daily_deaths_per_100k = row["DailyDeathsPer100k"] if "DailyDeathsPer100k" in row and not math.isnan(row["DailyDeathsPer100k"])  else None
        status.daily_cases_per_100k = row["DailyCasesPer100k"] if "DailyCasesPer100k" in row and not math.isnan(row["DailyCasesPer100k"])  else None
        status.day_norm = row["DayNorm"] if "DayNorm" in row and not math.isnan(row["DayNorm"])  else None
        status.growth_rate = row["GrowthRate"] if "GrowthRate" in row and not math.isnan(row["GrowthRate"])  else None
        status.growth_rate_deaths = row["GrowthRateDeaths"] if "GrowthRateDeaths" in row and not math.isnan(row["GrowthRateDeaths"])  else None
        status.days_to_double = row["DaysToDouble"] if "DaysToDouble" in row and not math.isnan(row["DaysToDouble"])  else None
        status.days_to_double_death = row["DaysToDoubleDeath"] if "DaysToDoubleDeath" in row and not math.isnan(row["DaysToDoubleDeath"])  else None
        status.weekly_growth = row["WeeklyGrowth"] if "WeeklyGrowth" in row and not math.isnan(row["WeeklyGrowth"])  else None
        status.weekly_growth_deaths = row["WeeklyGrowthDeaths"] if "WeeklyGrowthDeaths" in row and not math.isnan(row["WeeklyGrowthDeaths"])  else None
        status.save()


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