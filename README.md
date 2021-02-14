# How is my country doing?

This is a template site for comparing data of pandemics progression between places.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

The site is built with [Python 3](https://www.python.org/downloads/).
We use also [Pipenv](https://github.com/pypa/pipenv) to manage or dependencies.

### Installing

To run your project local:

Install the dependencies

```
pipenv install
```

Configure your `.env` file. This repository comes with an example config

```
cp .env.example .env
```

Enter the Pipenv virtual env

```
pipenv shell
```

Configure your database
```
pipenv run flask migrate up
```


Run the application

```
pipenv run flask run
```

Access http://localhost:5000 (or to the other port configured on your .env file) to see the running site.

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
