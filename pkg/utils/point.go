package utils

// Point.
type Point []float64

type PointSet struct {
	Points   []Point
	Labels   []float64
	RefPoint Point
}

func (p Point) Scale(factor float64) Point {
	pt := make(Point, len(p))
	for i, val := range p {
		pt[i] = factor * val
	}
	return pt
}

// Helper for computing the square distance between two points.
func Distance(p1, p2 Point) float64 {
	var sum float64
	for i, val := range p1 {
		sum += (val - p2[i]) * (val - p2[i])
	}
	return sum
}

// methods for sort.Interface
func (p PointSet) Len() int { return len(p.Points) }

func (p PointSet) Less(i, j int) bool {
	return Distance(p.RefPoint, p.Points[i]) < Distance(p.RefPoint, p.Points[j])
}

func (p PointSet) Swap(i, j int) {
	p.Points[i], p.Points[j] = p.Points[j], p.Points[i]
	p.Labels[i], p.Labels[j] = p.Labels[j], p.Labels[i]
}
