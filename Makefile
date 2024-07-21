GOFMT=$(shell go env GOPATH)/bin/gofmt

format:
	@echo "Formatting Go code..."
	@gofmt -s -w .

.PHONY: format
