#!/bin/bash

source ~/.bash_profile

pyenv activate waffle-backend

cd ~/waffle-rookies-18.5-backend-2

git pull origin deploy

FILE=/home/ec2-user/waffle-rookies-18.5-backend-2/requirements.txt
if test -f "$FILE"; then
	echo "$FILE exists. Pip-Installing it..."
	pip install -r $FILE
else
	echo "$FILE does not exist."
fi	

cd ~/waffle-rookies-18.5-backend-2/waffle_backend

python manage.py migrate

python manage.py check --deploy

cd ~/

redis-server --daemonize yes

uwsgi --ini /home/ec2-user/waffle-rookies-18.5-backend-2/waffle_backend/waffle-backend_uwsgi.ini

sudo nginx -t

sudo service nginx restart

