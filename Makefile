postbuild:
	- docker-compose exec server python manage.py migrate
	- docker-compose exec server python manage.py createsuperuser
