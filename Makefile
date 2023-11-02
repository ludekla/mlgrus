CMD = $(wildcard cmd/*.go)
.PHONY: vet-cmd $(CMD)

all: fmt vet vet-cmd test

fmt:
	go fmt ./...

vet:
	go vet ./pkg/...

vet-cmd: $(CMD)

$(CMD):
	go vet $@

test:
	go test ./pkg/...

test-v:
	go test -v ./pkg/...

clean:
	rm bin/* 