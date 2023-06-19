package tree

import (
	"encoding/json"
	"encoding/csv"
	"os"
	"io/ioutil"
	"log"
	"math"
)

type Candidate struct {
	Level   string  `json:"level"`
	Lang    string	`json:"lang"`
	Tweets  bool	`json:"tweets"`
	PhD     bool	`json:"phd"`
	DidWell bool	`json:"didwell"`
}

func (c *Candidate) Get(attr string) interface{} {
	switch attr {
	case "level":
		return c.Level
	case "lang":
		return c.Lang
	case "tweets":
		return c.Tweets
	case "phd":
		return c.PhD
	case "didwell":
		return c.DidWell
	default:
		return nil
	}
}

type Partition map[interface{}][]*Candidate

func fromJSON(jsnfile string) []*Candidate {
	var cands []*Candidate
	data, err := ioutil.ReadFile(jsnfile)
	if err != nil {
		log.Fatalf("cannot read file %s, error: %v\n", jsnfile, err)
	}
	err = json.Unmarshal(data, &cands)
	if err != nil {
		log.Fatal(err)
	}
	return cands
}

func FromCSV(csvfile string) []*Candidate {
	var cands []*Candidate
	file, err := os.Open(csvfile)
	if err != nil {
		log.Fatal(err)
	}
	defer file.Close()
	reader := csv.NewReader(file)
	records, err := reader.ReadAll()
	if err != nil {
		log.Fatal(err)
	}
	for _, record := range records[1:] {
		cand := &Candidate{Level: record[0], Lang: record[1]}
		if record[2] == "1" {
			cand.Tweets = true
		}
		if record[3] == "1" {
			cand.PhD = true
		}
		if record[4] == "1" {
			cand.DidWell = true
		}
		cands = append(cands, cand)
	}
	return cands
}

func clsprobs(data []interface{}) []float64 {
	total := float64(len(data))
	count := map[interface{}]int{}
	for _, item := range data {
		count[item] += 1
	}
	i := 0
	ps := make([]float64, len(count))
	for _, v := range count {
		ps[i] = float64(v) / total
		i++
	}
	return ps
}

func entropy(probs []float64) float64 {
	sum := 0.0
	for _, prob := range probs {
		if prob > 0 {
			sum -= prob * math.Log2(prob)
		}
	}
	return sum
}

func DataEntropy(data []interface{}) float64 {
	return entropy(clsprobs(data))
}

func PartitionBy(cands []*Candidate, attr string) Partition {
	partition := make(Partition)
	for _, cand := range cands {
		value := cand.Get(attr)
		if value != nil {
			partition[value] = append(partition[value], cand)
		}
	}
	return partition
}

func PartitionEntropyBy(partition Partition, attr string) float64 {
	sum := 0.0
	N := 0
	for _, subset := range partition {
		n := len(subset)
		N += n
		data := make([]interface{}, n)
		for i, cand := range subset {
			data[i] = cand.Get(attr)
		}
		sum += float64(n) * DataEntropy(data)
	}
	return sum / float64(N)
}

type Tree struct {
	attrib   string
	value    bool
	branches Branches
}

type Branches map[interface{}]*Tree

func New(attr string, val bool, b Branches) *Tree {
	return &Tree{attrib: attr, value: val, branches: b}
}

func (t *Tree) Classify(cand *Candidate) bool {
	if t.branches == nil {
		return t.value
	}
	if b, ok := t.branches[cand.Get(t.attrib)]; ok {
		return b.Classify(cand)
	} else {
		return t.value
	}
}

func BuildTree(cands []*Candidate, splitAttrs []string, targetAttr string) *Tree {
	labels := make(map[interface{}]int)
	for _, cand := range cands {
		val := cand.Get(targetAttr)
		labels[val] += 1
	}
	max := 0
	var mostCommon interface{}
	for label, count := range labels {
		if count > max {
			mostCommon = label
			max = count
		}
	}
	if len(labels) == 1 || len(splitAttrs) == 0 {
		return New("", mostCommon.(bool), nil)
	}
	var bestAttr string
	var bestPartition Partition
	min := 1.0
	for _, attr := range splitAttrs {
		partition := PartitionBy(cands, attr)
		imp := PartitionEntropyBy(partition, targetAttr)
		if imp < min {
			min = imp
			bestAttr = attr
			bestPartition = partition
		}
	}
	attrs := make([]string, 0, len(splitAttrs) - 1)
	for _, attr := range splitAttrs {
		if attr != bestAttr {
			attrs = append(attrs, attr)
		}
	}
	branches := make(Branches)
	for val, subset := range bestPartition {
		branches[val] = BuildTree(subset, attrs, targetAttr)
	}
	return New(bestAttr, mostCommon.(bool), branches)
}
