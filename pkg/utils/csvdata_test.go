package utils

import (
	"testing"
)

func TestCSVFloat(t *testing.T) {
	csv := NewCSVData("../../data/csv/test_utils.csv", true, AtoF)
	header := []string{"A", "B", "C", "T"}
	for i, ch := range csv.Header {
		if ch != header[i] {
			t.Errorf("expected %s, got %s", header[i], ch)
		}
	}
	rows := [][]float64{{1.1, -2.4, 8.9, 1.0}, {-10.2, 2.2, -0.1, 0.0}}
	for i, row := range csv.Records {
		for j, val := range row {
			if val != rows[i][j] {
				t.Errorf("expected %v, got %v", rows[i][j], val)
			}
		}
	}
}

func TestCSVString(t *testing.T) {
	csv := NewCSVData("../../data/csv/test_utils.csv", false, AtoA)
	rows := [][]string{
		{"A", "B", "C", "T"},
		{"1.1", "-2.4", "8.9", "1"},
		{"-10.2", "2.2", "-0.1", "0"},
	}
	for i, row := range csv.Records {
		for j, val := range row {
			if val != rows[i][j] {
				t.Errorf("expected %v, got %v", rows[i][j], val)
			}
		}
	}
}
