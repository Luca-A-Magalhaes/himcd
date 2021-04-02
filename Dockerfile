FROM "python:3.8.5"

RUN pip3 install pipenv

COPY . /app

WORKDIR /app

RUN pipenv install

CMD ["pipenv", "run", "sh", "./gunicorn.sh"]