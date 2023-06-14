package knn

import (
	"math"
	"math/rand"
	"sort"
	"time"

	ut "mlgrus/pkg/utils"
)

func init() {
	rand.Seed(time.Now().Unix())
}

type KNNClassifier struct {
	nNeighs int
	ptset   ut.PointSet
}

func NewKNNClassifier(k int) *KNNClassifier {
	return &KNNClassifier{nNeighs: k}
}

func (c *KNNClassifier) Fit(pts []ut.Point, lbs []float64) {
	c.ptset = ut.PointSet{Points: pts, Labels: lbs}
}

func (c *KNNClassifier) Predict(points []ut.Point) []float64 {
	labels := make([]float64, len(points))
	for i, point := range points {
		c.ptset.RefPoint = point
		sort.Sort(c.ptset)
		labels[i] = c.vote()
	}
	return labels
}

func (c *KNNClassifier) vote() float64 {
	var mean float64
	for i, _ := range c.ptset.Points[:c.nNeighs] {
		mean += c.ptset.Labels[i]
	}
	mean /= float64(c.nNeighs)
	return math.Round(mean)
}

func (c *KNNClassifier) Score(points []ut.Point, labels []float64) float64 {
	preds := c.Predict(points)
	var ct float64
	for i, pred := range preds {
		if pred == labels[i] {
			ct++
		}
	}
	return ct / float64(len(points))
}
