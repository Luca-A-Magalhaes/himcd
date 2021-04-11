# How is my country doing?

This is a template site for comparing data of pandemics progression between places.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Downloading

First, download the source code by cloning this repository:

```
git clone https://github.com/Luca-A-Magalhaes/himcd
```

### Configuring the database

The project uses [MySQL](https://www.mysql.com/downloads/) as default database engine, you will need an instance running with a database for the project. If you want to change to another engine refer to [SQLAlchemy Manual](https://docs.sqlalchemy.org/en/14/core/engines.html).

Also if you dont want to setup an database initially, you can use an development database provide on the [Using Docker](#using-docker) setup. WARNING: we DO NOT recommend using this database on production environment, since all database data WILL BE WIPED on the container removal.


### Using Docker

We recommend using [Docker](https://www.docker.com/) to facilitate the configuration of the project.

After [installing the Docker engine](https://www.docker.com/get-started), edit `environment` section in `docker-compose.yaml` (line 13) with your database connection. If you're running the database locally, leave the `DB_HOST` set to `host.docker.internal`.

If you dont have database runnning. Comment lines 14-18 of `docker-compose.yaml` and uncomment lines 19-31 to use a development mysql database.

Then you can run (Notice: this can take a while depending on how much resources you enabled for Docker).

```
docker-compose up -d
```

After the container finished building, configure the database with:

```
docker exec himcd pipenv run flask migrate up
```

and access http://localhost:5000



## Using Pipenv

Also you can use [Pipenv](https://github.com/pypa/pipenv) to install and run the project.

First, install the dependencies

```
pipenv install
```

Configure your `.env` file. This repository comes with an example config. Please fill in the correct connection to your database

```
cp .env.example .env
```

Configure your database
```
pipenv run flask migrate up
```

Run the application using the flask webserver

```
pipenv run flask run
```

Or using Gunicorn WSGY

```
pipenv run sh ./gunicorn.sh
```

Access http://localhost:5000 (or to the other port configured on your .env file) to see the running site.

### Templates structure

The project provides pré-built pages structures and components, inside the `app/templates` folder.

To start a new page you can rename the example page at `app/templates/pages/page.html.jinja`.

## Data

The project provides an interface to import pandemic data into the database. Use the `data/` folder to store your CSV files.

You can do so with the command

```
pipenv run flask data load data/file.csv
```

Or if you are using Docker

```
docker exec himcd pipenv run flask data load data/file.csv
```

The command will take the file csv data and add to the `Country` and `CountryStatus` tables.

Note the command by default will only append new data, not update or delete previous data.

But you can pass the `--override` flag to erase all previous data before importing.

We provide a `data/sample_data.csv` file as an example of data accepted.

The file content format is

```
'Country Name', 'Date', 'Total', 'Day' (days since beginning of the pandemic), 'TotalDeaths', 'TotalPer100k', 'TotalDeathsPer100k', 'DayNorm' (days since country's 10th death, 'GrowthRate' (increase factor from previous day), 'GrowthRateDeaths', 'DaysToDouble' (number of days to double cases based on current rate), 'DaysToDoubleDeaths', 'WeeklyGrowth' (percentage of growth in the previous 7 days), 'WeeklyGrowthDeaths'
```

## Translations

To contribute to the translations section follow the steps:

### Markdown

To markdown text to translation you have to use the `_l()` and `_()` functions from the `flask-babel` library. Use the `_l()` function to mark strings outside a request handler (routes functions or templates). And use `_()` function to mark string inside a request handler

Ex:

`/app/templates/about_us.html`
```
...

<h2>{{ _('The Project') }}</h2>

...
```

`/app/forms.py`
```
from flask_babelex import lazy_gettext as _l
...

submit = SubmitField(_l('Show Report'))

...
```

### Translation and localization

To translate added texts, first we need to update the translations folders with the command:


```
pipenv run flask translate update
```

Now access the `messages.po` file corresponding to the language you want to translate. Their are located on the folder `/translations/<language>/LC_MESSAGES/`
Place under the text on English the translation.

Ex:

`/translations/pt_br/LC_MESSAGES/messages.po`

```
...

#: app/templates/about_us.html:6
msgid "The Project"
msgstr "O Projeto"

...

#: app/forms.py:11 app/forms.py:16
msgid "Show Report"
msgstr "Mostrar Relatório"

...
```

### Compiling

To compile all translations and effect all changes, just run the command:

```
pipenv run flask translate compile
```

## Authors

The people behind the site are:

- Guilmor Rossi
- Luca Almeida
- Luiz Celso Gomes Jr
- Nicole Kobayashi
- Vitor Corrêa
- Zulmira Coimbra

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details
