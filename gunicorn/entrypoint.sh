#!/bin/bash
cd /root/web_project
python3 manage.py makemigrations
python3 manage.py migrate
python3 manage.py collectstatic --noinput
echo "
from django.contrib.auth.models import User
try:
    User.objects.create_superuser('admin', 'admin@example.com', 'admin')    
except:
    print('Default User Created')    
    " | python3 /root/web_project/manage.py shell

gunicorn --chdir /root/web_project --certfile=/root/certs/sparkligth.nso.crt --keyfile=/root/certs/sparkligth.nso.key -b 0.0.0.0:8000 web_project.wsgi
# python3 manage.py runserver 0.0.0.0:8000
