GOFMT=$(shell go env GOPATH)/bin/gofmt

format:
	@echo "Formatting Go code..."
	@gofmt -s -w .

start:
	docker compose down
	if [ "${DEBUG}" = true ]; then \
		docker compose up --build; \
	else \
		docker compose up --build --detach; \
	fi

stop:
	docker compose down

install:
	pip3 install -r requirements.txt

test-build:
	docker compose -f postgres.yml down
	docker compose -f postgres.yml up --build

.PHONY: format start stop install
