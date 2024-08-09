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

.PHONY: format start stop
