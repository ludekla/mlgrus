package knn

// Point.
type Point []float64

type PointSet struct {
	points   []Point
	labels   []float64
	refpoint Point
}

// Helper for computing the distance between two points.
func dist(p1, p2 Point) float64 {
	var sum float64
	for i, val := range p1 {
		sum += (val - p2[i]) * (val - p2[i])
	}
	return sum
}

// methods for sort.Interface
func (p PointSet) Len() int { return len(p.points) }

func (p PointSet) Less(i, j int) bool {
	return dist(p.refpoint, p.points[i]) < dist(p.refpoint, p.points[j])
}

func (p PointSet) Swap(i, j int) {
	p.points[i], p.points[j] = p.points[j], p.points[i]
	p.labels[i], p.labels[j] = p.labels[j], p.labels[i]
}
