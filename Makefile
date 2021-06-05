postbuild:
	- docker-compose exec server python manage.py makemigrations
	- docker-compose exec server python manage.py migrate
	- docker-compose exec server python manage.py createsuperuser

loaddata:
	- docker-compose exec server python manage.py init
