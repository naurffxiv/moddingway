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

database-clean:
	docker exec postgres_db rm scripts -r -f
	docker exec postgres_db mkdir scripts
	docker cp postgres postgres_db:scripts
	docker exec postgres_db psql -f scripts/postgres/drop_all_tables.sql -U moddingwayLocalDB moddingway
	docker exec postgres_db psql -f scripts/postgres/create_tables.sql -U moddingwayLocalDB moddingway
	docker exec postgres_db psql -f scripts/postgres/seed_data.sql -U moddingwayLocalDB moddingway

.PHONY: format stop install clean python-build python-run database-run
