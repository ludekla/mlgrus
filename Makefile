
fmt:
	go fmt pkg/utils/*
	go fmt pkg/knn/*
	go fmt pkg/cluster/*
	go fmt pkg/tree/*

vet:
	go vet pkg/utils/*
	go vet pkg/knn/*
	go vet pkg/cluster/*
	go vet pkg/tree/*

test:
	go test pkg/utils/*

clean:
	rm bin/*
