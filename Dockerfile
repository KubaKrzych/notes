FROM python

WORKDIR /app

COPY . /app

RUN apt-get update && apt-get install -y python3 python3-pip && pip install -r requirements.txt

RUN 

ENTRYPOINT python manage.py collectstatic --noinput && gunicorn notes.wsgi:application --bind 0.0.0.0:8000