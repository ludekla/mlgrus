package cluster

import (
	"math"
	"math/rand"

	ut "mlgrus/pkg/utils"
)

func clustMean(cluster []ut.Point) ut.Point {
	size := len(cluster)
	if size == 0 {
		panic("cannot compute mean of empty cluster")
	}
	mean := make(ut.Point, len(cluster[0]))
	for _, pt := range cluster {
		for i, val := range pt {
			mean[i] += val
		}
	}
	return mean.Scale(1.0 / float64(size))
}

func clusterMeans(k int, inputs []ut.Point, labels []int) map[int]ut.Point {
	nInputs := len(inputs)
	if nInputs != len(labels) {
		panic("number of labels does not match number of data points")
	}
	clusters := make(map[int][]ut.Point)
	for i, label := range labels {
		clusters[label] = append(clusters[label], inputs[i])
	}
	kMeans := make(map[int]ut.Point)
	for i := 0; i < k; i++ {
		if clusters[i] == nil {
			choice := rand.Intn(nInputs)
			kMeans[i] = inputs[choice]
		} else {
			kMeans[i] = clustMean(clusters[i])
		}
	}
	return kMeans
}

type KMeans struct {
	k     int
	Means map[int]ut.Point
}

func NewKMeans(nClusters int) *KMeans {
	return &KMeans{k: nClusters}
}

func (km *KMeans) Classify(pt ut.Point) int {
	var min = math.MaxFloat64
	var label int
	for i, mean := range km.Means {
		dist := ut.Distance(pt, mean)
		if dist < min {
			min = dist
			label = i
		}
	}
	return label
}

func (km *KMeans) Fit(data []ut.Point) float64 {
	labels := make([]int, len(data))
	for i, _ := range labels {
		labels[i] = rand.Intn(km.k)
	}
	var ct int = 1
	for ct > 0 {
		km.Means = clusterMeans(km.k, data, labels)
		ct = 0
		for i, pt := range data {
			newLabel := km.Classify(pt)
			if labels[i] != newLabel {
				labels[i] = newLabel
				ct++
			}
		}
	}
	return km.MSE(data, labels)
}

// Mean Square Error
func (km *KMeans) MSE(data []ut.Point, labels []int) float64 {
	var sum float64
	for i, label := range labels {
		sum += ut.Distance(data[i], km.Means[label])
	}
	return math.Sqrt(sum / float64(len(labels)))
}
