package main

import (
	"fmt"
	"math/rand"
	"time"
	"os"
	"encoding/csv"
	"strconv"
	"image"
	"image/jpeg"
	"image/color"
)

func init() {
	now := time.Now()
	rand.Seed(int64(now.Second()))
}

type Vector []float64

func (vec Vector) Scale(factor float64) Vector {
	rvec := make(Vector, len(vec))
	for i, val := range vec {
		rvec[i] = factor * val
	}
	return rvec
}

func squareDist(lvec Vector, rvec Vector) float64 {
	var sum float64
	for i, val := range rvec {
		sum += (lvec[i] - val) * (lvec[i] - val)
	}
	return sum
}

func clustMean(cluster []Vector) Vector {
	size := len(cluster)
	if size == 0 {
		panic("cannot compute mean of empty cluster")
	}
	mean := make(Vector, len(cluster[0]))
	for _, vec := range cluster {
		for i, val := range vec {
			mean[i] += val 
		}
	}
	return mean.Scale(1.0/float64(size))
}

func clusterMeans(k int, inputs []Vector, labels []int) map[int]Vector {
	nInputs := len(inputs)
	if nInputs != len(labels) {
		panic("number of labels does not match number of data points")
	}
	clusters := make(map[int][]Vector)
	for i, label := range labels {
		clusters[label] = append(clusters[label], inputs[i])
	}
	kMeans := make(map[int]Vector)
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
	k  int
	means map[int]Vector 
}

func NewKMeans(nClusters int) *KMeans {
	return &KMeans{k: nClusters}
}

func (km *KMeans) Classify(vec Vector) int {
	var min = squareDist(vec, km.means[0])
	var label int
	for i, mean := range km.means {
		if i == 0 {
			continue
		}
		dist := squareDist(vec, mean)
		if dist < min {
			min = dist
			label = i
		}
	}
	return label
}

func (km *KMeans) Fit(data []Vector) float64 {
	labels := make([]int, len(data))
	for i, _ := range labels {
		labels[i] = rand.Intn(km.k)
	}
	ct := 0
	var changed bool = true
	for changed {
		fmt.Printf("round %d\n", ct)
		changed = false
		km.means = clusterMeans(km.k, data, labels)
		for i, vec := range data {
			newLabel := km.Classify(vec)
			if !changed && labels[i] != newLabel {
				changed = true
			}
			labels[i] = newLabel
		}
		ct++
	}
	return km.squareError(data, labels)
}

func (km *KMeans) squareError(data []Vector, labels []int) float64 {
	var sum float64
	for i, label := range labels {
		sum += squareDist(data[i], km.means[label])
	}
	return sum
}

func getData(filename string) []Vector {
	file, err := os.Open(filename)
	if err != nil {
		panic("Shit: cannot open the file")
	}
	defer file.Close()
	reader := csv.NewReader(file)
	records, err := reader.ReadAll()
	if err != nil {
		panic("csv reader failed")
	}
	vecs := make([]Vector, len(records))
	for i, record := range records {
		vec := make(Vector, len(record))
		for j, val := range record {
			vec[j], err = strconv.ParseFloat(val, 64)
			if err != nil {
				panic("cannot parse float")
			}
		}
		vecs[i] = vec
	}
	return vecs
}

func kMeansError(k int, data []Vector) float64 {
	km := NewKMeans(k)
	return km.Fit(data)
}

func loadImage(filename string) image.Image {
	imgfile, err := os.Open(filename)
	if err != nil {
		panic("cannot open picture")
	}
	defer imgfile.Close()
	img, err := jpeg.Decode(imgfile)
	if err != nil {
		panic("cannot decode the file")
	}
	return img
}

func getPixelData(img image.Image) []Vector {
	size := img.Bounds().Size()
	width, height := size.X, size.Y
	pixels := make([]Vector, width*height)
	for x := 0; x < height; x++ {
		for y := 0; y < width; y++ {
			r, g, b, _ := img.At(x, y).RGBA()
			pixels[x*width + y] = Vector{float64(r), float64(g), float64(b)} 
		}
	}
	return pixels
}

func transformImage(km *KMeans, img image.Image) image.Image {
	if km.means == nil {
		panic("Please first train the k-means engine!")
	}
	size := img.Bounds().Size()
	height, width := size.X, size.Y
	newImg := image.NewRGBA64(image.Rect(0, 0, size.X, size.Y))
	for x := 0; x < height; x++ {
		for y := 0; y < width; y++ {
			r, g, b, a := img.At(x, y).RGBA()
			vec := Vector{float64(r), float64(g), float64(b)}
			clusterID := km.Classify(vec)
			pixel := km.means[clusterID]
			colour := color.RGBA64{
				uint16(pixel[0]), uint16(pixel[1]), uint16(pixel[2]), uint16(a),
			}
			newImg.SetRGBA64(x, y, colour)
		}
	}
	return newImg
}

func main() {

	data := getData("loci.csv")

	m := len(data)
	errors := make(Vector, m)
	for k, _ := range errors {
		errors[k] = kMeansError(k + 1, data)
	}
	fmt.Println(errors)

	img := loadImage("lutz.jpg")
	pixels := getPixelData(img)
	
	km := NewKMeans(5)
	e := km.Fit(pixels)
	fmt.Printf("%v %v\n", e, km.means)

	newImg := transformImage(km, img)
	outFile, err := os.Create("lutz6.jpg")
	if err != nil {
		panic("SHIT: cannot create image file")
	}
	jpeg.Encode(outFile, newImg, nil)
	outFile.Close()

} 