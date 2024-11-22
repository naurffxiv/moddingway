format:
	python3 -m black .

stop:
	docker compose down

install:
	pip3 install -r requirements.txt

clean:
	docker image prune -a

python-build:
	docker compose build python-app

python-run:
	docker compose down
	docker compose up python-app-local --build

database-run:
	docker compose -f postgres.yml up -d

api-build:
	python3 server/manage.py makemigrations
	python3 server/manage.py migrate

api-run:
	python3 server/manage.py runserver

.PHONY: format stop install clean python-build python-run database-run
