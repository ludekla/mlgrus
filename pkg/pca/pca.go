package main

import (
	"fmt"
	"encoding/csv"
	"os"
	"strconv"
	"math"
	"math/rand"
)

// data vector
type Vector []float64

func (vec Vector) Dot(ovec Vector) float64 {
	if len(vec) != len(ovec) {
		fmt.Println("ERROR: vectors must be of the same dimension")
		os.Exit(1)
	}
	var sum float64
	for i, val := range vec {
		sum += ovec[i] * val
	}
	return sum
}

func NewVector(n int) Vector {
	vec := make(Vector, n)
	for i := 0; i < n; i++ {
		vec[i] = rand.NormFloat64()
	}
	return vec
}

func loadData(filename string) ([]Vector, []int) {
	file, err := os.Open("iris.csv")
	if err != nil {
		panic(err)
	}
	defer file.Close()
	reader := csv.NewReader(file)
	records, err := reader.ReadAll()
	if err != nil {
		panic(err)
	}
	X := make([]Vector, len(records))
	y := make([]int, len(records))
	for i, record := range records {
		n := len(record)
		x := make(Vector, n-1)
		for j, item := range record[:n-1] {
			x[j], err = strconv.ParseFloat(item, 64)
			if err != nil {
				fmt.Println("failed to convert element %d in line %d", j, i)
				continue
			}
		}
		X[i] = x
		val, err := strconv.ParseInt(record[n-1], 0, 0)
		if err != nil {
			fmt.Println("failed to parse label in line %d", i)
		}
		y[i] = int(val)  // int64 -> int
	}
	return X, y
}

func demean(data []Vector) []Vector {
	means := make(Vector, len(data[0]))
	for _, row := range data {
		for j, elem := range row {
			means[j] += elem
		}
	}
	N := len(data)
	for i, val := range means {
		means[i] = val / float64(N)
	}
	centred := make([]Vector, len(data))
	for i, row := range data {
		rowc := make(Vector, len(row))  // centred row
		for j, elem := range row {
			rowc[j] = elem - means[j]
		}
		centred[i] = rowc
	}
	return centred
}

func magnitude(vec Vector) float64 {
	var sum float64
	for _, comp := range vec {
		sum += comp * comp
	}
	return math.Sqrt(sum)
}

func direction(vec Vector) Vector {
	mag := magnitude(vec)
	direc := make(Vector, len(vec))
	for i, comp := range vec {
		direc[i] = comp / mag
	}
	return direc
}

func dirVar(data []Vector, vec Vector) float64 {
	var sum float64
	direc := direction(vec) 
	for _, x := range data {
		z := direc.Dot(x)
		sum += z * z
	}
	return sum
}

func dirVarGrad(data []Vector, vec Vector) Vector {
	direc := direction(vec)
	u := make(Vector, len(data))
	for i, x := range data {
		u[i] = x.Dot(direc)
	}
	z := make(Vector, len(vec))
	for i, _ := range vec {
		var sum float64
		for j, val := range u {
			sum += val * data[j][i]
		}
		z[i] = 2 * sum
	}
	return z
}

func FirstPC(data []Vector, nRounds int, stepSize float64) Vector {
	if len(data) == 0 {
		panic("shithead")
	}
	guess := NewVector(len(data[0]))
	for r := 0; r < nRounds; r++ {
		grad := dirVarGrad(data, guess)
		for i, val := range guess {
			guess[i] = val - stepSize * grad[i]
		}
	}
	return direction(guess)
}

func project(direc Vector, vec Vector) Vector {
	pvec := make(Vector, len(direc))
	mag := direc.Dot(vec)
	for i, val := range direc {
		pvec[i] = mag * val
	}
	return pvec
}

func project2comp(direc Vector, vec Vector) Vector {
	pvec := project(direc, vec)
	for i, val := range pvec {
		pvec[i] = vec[i] - val
	}
	return pvec
}

func projectem2comp(direc Vector, data []Vector) []Vector {
	tdata := make([]Vector, len(data))
	for i, vec := range data {
		tdata[i] = project2comp(direc, vec)
	}
	return tdata
}

func PCA(data []Vector, nComps int) []Vector {
	components := make([]Vector, nComps)
	for i := 0; i < nComps; i++ {
		pc := FirstPC(data, 200, 0.1)
		components[i] = pc
		data = projectem2comp(pc, data)
	}
	return components
}

func transform(comps []Vector, vec Vector) Vector {
	tvec := make(Vector, len(comps))
	for i, comp := range comps {
		tvec[i] = comp.Dot(vec)
	}
	return tvec
}

func transformem(comps []Vector, data []Vector) []Vector {
	tvecs := make([]Vector, len(data))
	for i, vec := range data {
		tvecs[i] = transform(comps, vec)
	}
	return tvecs
}

func main() {

	X, _ := loadData("iris.csv")

	Xcentred := demean(X)

	comps := PCA(Xcentred, 3)
	for i, comp := range comps {
		fmt.Printf("pc %d: %v\n", i + 1, comp)
	}

	tdata := transformem(comps, Xcentred)
	for i, v := range tdata[:10] {
		fmt.Printf("vec %d: %v\n", i, v)
	}

	tvec := transform(comps, Xcentred[0])
	fmt.Printf("%v -> %v\n", Xcentred[0], tvec)
	
}

