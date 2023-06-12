
fmt:
	go fmt pkg/utils/*
	go fmt pkg/knn/*

vet:
	go vet pkg/utils/*
	go vet pkg/knn/*

test:
	go test pkg/utils/*

clean:
	rm bin/*
