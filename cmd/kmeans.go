package main

import (
    "fmt"

    "mlgrus/pkg/cluster"
    "mlgrus/pkg/utils"
)

func kMeansError(k int, data []utils.Point) float64 {
	km := cluster.NewKMeans(k)
	return km.Fit(data)
}

func main() {

	data := utils.NewCSVData("data/loci.csv", false, utils.AtoF)
    points := utils.Transform(data.Records)
	size := data.Size()

	errors := make([]float64, size)
	for k, _ := range errors {
		errors[k] = kMeansError(k + 1, points)
	}
	fmt.Println(errors)

}
