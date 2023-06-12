package knn

import (
	"math"
	"math/rand"
	"sort"
	"time"
)

func init() {
	rand.Seed(time.Now().Unix())
}

type KNNClassifier struct {
	nNeighs int
	ptset   PointSet
}

func NewKNNClassifier(k int) *KNNClassifier {
	return &KNNClassifier{nNeighs: k}
}

func (c *KNNClassifier) Fit(pts []Point, lbs []float64) {
	c.ptset = PointSet{points: pts, labels: lbs}
}

func (c *KNNClassifier) Predict(points []Point) []float64 {
	labels := make([]float64, len(points))
	for i, point := range points {
		c.ptset.refpoint = point
		sort.Sort(c.ptset)
		labels[i] = c.vote()
	}
	return labels
}

func (c *KNNClassifier) vote() float64 {
	var mean float64
	for i, _ := range c.ptset.points[:c.nNeighs] {
		mean += c.ptset.labels[i]
	}
	mean /= float64(c.nNeighs)
	return math.Round(mean)
}

func (c *KNNClassifier) Score(points []Point, labels []float64) float64 {
	preds := c.Predict(points)
	var ct float64
	for i, pred := range preds {
		if pred == labels[i] {
			ct++
		}
	}
	return ct / float64(len(points))
}
