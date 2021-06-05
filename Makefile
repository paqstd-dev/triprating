postbuild:
	- docker-compose exec server python manage.py makemigrations
	- docker-compose exec server python manage.py migrate

loaddata:
	- docker-compose exec server python manage.py init
