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
	docker compose down python-app-local
	docker compose up python-app-local --build

database-run:
	docker compose -f postgres.yml up -d

.PHONY: format stop install clean python-build python-run database-run
