
fmt:
	go fmt pkg/utils/*
	go fmt pkg/knn/*
	go fmt pkg/cluster/*

vet:
	go vet pkg/utils/*
	go vet pkg/knn/*
	go vet pkg/cluster/*

test:
	go test pkg/utils/*

clean:
	rm bin/*
