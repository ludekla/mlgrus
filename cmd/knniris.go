package main

import (
    "fmt"
    "math/rand"

    "mlgrus/pkg/knn"
    "mlgrus/pkg/utils"
)

func main() {

    data := utils.NewCSVData("data/iris.csv", false, utils.AtoF)

	rand.Shuffle(len(data.Records), func(i, j int){
		data.Records[j], data.Records[i] = data.Records[i], data.Records[j]
	})

    points := make([]knn.Point, len(data.Records))
    labels := make([]float64, len(data.Records))
    for i, record := range data.Records {
        points[i] = knn.Point(record[:4])
        labels[i] = record[4]
    }

    clf := knn.NewKNNClassifier(5)

    clf.Fit(points[:100], labels[:100])

    acc := clf.Score(points[100:], labels[100:])

    fmt.Printf("Accuracy: %.3f - Test size: %d\n", acc, len(labels[100:]))

    for i, pred := range clf.Predict(points[:20]) {
        fmt.Printf("label: %f predicted: %f\n", labels[i], pred)
    }

}
