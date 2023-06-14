package utils

import (
	"encoding/csv"
	"fmt"
	"log"
	"os"
	"strconv"
)

type Row[T any] []T

type Converter[T any] func([]string) (Row[T], error)

type CSVData[T any] struct {
	Header  []string
	Records []Row[T]
}

func AtoF(rec []string) (Row[float64], error) {
	row := make(Row[float64], len(rec))
	for i, strval := range rec {
		val, err := strconv.ParseFloat(strval, 64)
		if err != nil {
			return nil, fmt.Errorf("cannot convert col %d: %v", i, err)
		}
		row[i] = val
	}
	return row, nil
}

func AtoA(rec []string) (Row[string], error) {
	return Row[string](rec), nil
}

func NewCSVData[T any](path string, header bool, conv Converter[T]) CSVData[T] {
	fp, err := os.Open(path)
	if err != nil {
		log.Fatalf("cannot open file: %v", err)
	}
	defer fp.Close()
	rd := csv.NewReader(fp)
	var head []string
	if header {
		head, err = rd.Read()
		if err != nil {
			log.Fatalf("cannot read first line: %v", err)
		}
	}
	recs, err := rd.ReadAll()
	if err != nil {
		log.Fatalf("problem reading records: %v", err)
	}
	rows := make([]Row[T], 0, len(recs))
	for i, rec := range recs {
		row, err := conv(rec)
		if err != nil {
			fmt.Printf("failed reading row %d: %v\n", i, err)
		} else {
			rows = append(rows, row)
		}
	}
	return CSVData[T]{Header: head, Records: rows}
}

func (c CSVData[T]) Size() int {
	return len(c.Records)
}

func Transform(data []Row[float64]) []Point {
	pts := make([]Point, len(data))
	for i, row := range data {
		pts[i] = Point(row)
	}
	return pts
}
