package main

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"log"
	"sort"
)

type Columns map[string]string

func (cols Columns) Copy() Columns {
	newCols := make(Columns)
	for k, v := range cols {
		newCols[k] = v
	}
	return newCols
}

func (cols Columns) Update(oCols Columns) {
	for k, v := range oCols {
		cols[k] = v
	}
}

type Row map[string]interface{}

func (row Row) Copy() Row {
	rowCopy := make(Row)
	for k, v := range row {
		rowCopy[k] = v
	}
	return rowCopy
}

func (row Row) Update(orow Row) {
	for k, v := range orow {
		row[k] = v
	}
}

type Predicate func(Row) bool

type Table struct {
	Cols    Columns
	Rows    []Row
	sortCol string
}

func NewTable(cols Columns, rows []Row) *Table {
	if rows == nil {
		return &Table{Cols: cols, Rows: make([]Row, 0, 20)}
	}
	return &Table{Cols: cols, Rows: rows}
}

// implmentation of sort.Interface
func (tb *Table) Len() int {
	return len(tb.Rows)
}

func (tb *Table) Swap(i, j int) {
	tb.Rows[i], tb.Rows[j] = tb.Rows[j], tb.Rows[i]
}

func (tb *Table) Less(i, j int) bool {
	sortType, ok := tb.Cols[tb.sortCol]
	if !ok {
		panic("no column to sort by")
	}
	left, right := tb.Rows[i][tb.sortCol], tb.Rows[j][tb.sortCol]
	switch sortType {
	case "int":
		return left.(int) < right.(int)
	case "float64":
		return left.(float64) < right.(float64)
	case "string":
		return left.(string) < right.(string)
	default:
		return true
	}
}

func (tb *Table) String() string {
	txt := fmt.Sprintf("Table(\n   %v\n", tb.Cols)
	for _, row := range tb.Rows {
		txt += fmt.Sprintf("   %v\n", row)
	}
	return txt + ")"
}

func (tb *Table) typeCheck(row Row) {
	for key, value := range row {
		typename := fmt.Sprintf("%T", value)
		if tb.Cols[key] != typename {
			if typename == "float64" && tb.Cols[key] == "int" {
				// fmt.Println("type: ", typename)
				row[key] = int(value.(float64))
			} else if typename != "<nil>" {
				log.Fatalf("[TypeError] expected %v got %v", tb.Cols[key], typename)
			}
		}
	}
}

func (tb *Table) Get(i int) Row {
	return tb.Rows[i]
}

func (tb *Table) Insert(row Row) {
	if len(row) != len(tb.Cols) {
		panic("[InsertError] Row does not have correct number of entries")
	}
	tb.typeCheck(row)
	tb.Rows = append(tb.Rows, row)
}

func (tb *Table) Update(update Row, predicate Predicate) {
	if predicate == nil {
		predicate = func(row Row) bool { return true }
	}
	for _, row := range tb.Rows {
		if predicate(row) {
			for k, v := range update {
				row[k] = v
			}
		}
	}
}

func (tb *Table) Delete(predicate Predicate) {
	newRows := make([]Row, 0, tb.Len())
	for _, row := range tb.Rows {
		if !predicate(row) {
			newRows = append(newRows, row)
		}
	}
	tb.Rows = newRows
}

func (tb *Table) Where(predicate Predicate) *Table {
	ntb := NewTable(tb.Cols, nil)
	for _, row := range tb.Rows {
		if predicate(row) {
			ntb.Insert(row.Copy())
		}
	}
	return ntb
}

func (tb *Table) Limit(nRows int) *Table {
	ntb := NewTable(tb.Cols, make([]Row, nRows))
	for i, row := range tb.Rows {
		if i >= nRows {
			break
		}
		ntb.Rows[i] = row.Copy()
	}
	return ntb
}

type Calculation func(Row) float64

func (tb *Table) Select(
	keepCols []string, // columns to keep of the old ones
	addCols map[string]Calculation, // additional columns to compute
) *Table {
	var newCols = make(Columns)
	if keepCols == nil {
		keepCols = make([]string, 0, len(tb.Cols))
		for key, value := range tb.Cols {
			newCols[key] = value
			keepCols = append(keepCols, key)
		}
	} else {
		for _, key := range keepCols {
			newCols[key] = tb.Cols[key]
		}
	}
	for key := range addCols {
		newCols[key] = "float64"
	}
	newRows := make([]Row, tb.Len())
	for i, row := range tb.Rows {
		newRow := make(Row)
		for _, key := range keepCols {
			newRow[key] = row[key]
		}
		for key, fun := range addCols {
			newRow[key] = fun(row)
		}
		newRows[i] = newRow
	}
	return NewTable(newCols, newRows)
}

type Aggregators map[string]func([]Row) float64

func (tb *Table) GroupBy(
	groupByCols []string,
	aggregates Aggregators,
	having func([]Row) bool,
) *Table {
	if having == nil {
		having = func(rows []Row) bool { return true }
	}
	newCols := make(Columns)
	for _, key := range groupByCols {
		newCols[key] = tb.Cols[key]
	}
	for key, _ := range aggregates {
		newCols[key] = "float64"
	}
	groups := make(map[string][]Row)
	for _, row := range tb.Rows {
		txt := ""
		for _, key := range groupByCols {
			txt += fmt.Sprintf("%v", row[key])
		}
		groups[txt] = append(groups[txt], row)
	}
	newRows := make([]Row, 0, len(groups))
	for _, rows := range groups {
		if !having(rows) {
			continue
		}
		row := rows[0]
		newRow := make(Row)
		for _, key := range groupByCols {
			newRow[key] = row[key]
		}
		for key, aggregate := range aggregates {
			newRow[key] = aggregate(rows)
		}
		newRows = append(newRows, newRow)
	}
	return NewTable(newCols, newRows)
}

func (tb *Table) OrderBy(sortCol string) *Table {
	ntb := tb.Select(nil, nil)
	ntb.sortCol = sortCol
	sort.Sort(ntb)
	return ntb
}

func (tb *Table) Join(otherTb *Table, leftJoin bool) *Table {
	joinCols := make([]string, 0)
	addCols := make(Columns)
	for col, typ := range otherTb.Cols {
		if _, ok := tb.Cols[col]; !ok {
			addCols[col] = typ
		} else {
			joinCols = append(joinCols, col)
		}
	}
	newCols := tb.Cols.Copy()
	newCols.Update(addCols)
	ntb := NewTable(newCols, nil)
	for _, row := range tb.Rows {
		isJoin := func(orow Row) bool {
			for _, col := range joinCols {
				if row[col] != orow[col] {
					return false
				}
			}
			return true
		}
		otherRows := make([]Row, 0)
		for _, orow := range otherTb.Rows {
			if isJoin(orow) {
				otherRows = append(otherRows, orow)
			}
		}
		for _, orow := range otherRows {
			newRow := row.Copy()
			newRow.Update(orow)
			ntb.Insert(newRow)
		}
		if leftJoin && len(otherRows) == 0 {
			newRow := row.Copy()
			for k, _ := range addCols {
				newRow[k] = nil
			}
			ntb.Insert(newRow)
		}
	}
	return ntb
}

func sumUids(rows []Row) float64 {
	sum := 0.0
	for _, row := range rows {
		sum += float64(row["userID"].(int))
	}
	return sum
}

func main() {

	users := NewTable(
		Columns{"userID": "int", "name": "string", "nfriends": "int"}, // columns
		nil,
	)

	bytes, err := ioutil.ReadFile("data.json")
	if err != nil {
		panic(err)
	}
	data := make([]Row, 0, 20)
	err = json.Unmarshal(bytes, &data)
	for _, row := range data {
		users.Insert(row)
	}
	fmt.Println("created:\n", users)
	fmt.Println("before update", users.Get(1))
	users.Update(
		Row{"nfriends": 3},
		func(row Row) bool { return row["userID"].(int) == 1 })
	fmt.Println("after update", users.Get(1))

	dunn := users.Where(func(row Row) bool { return row["nfriends"].(int) == 3 })
	fmt.Println("dunn ids:\n", dunn)

	users.Delete(func(row Row) bool { return row["userID"].(int) == 1 })
	fmt.Println("delete:\n", users)

	uids := users.Select([]string{"userID", "name"}, nil)
	fmt.Println("select:\n", uids)
	lowIds := uids.Where(func(row Row) bool { return row["userID"].(int) < 6 })
	fmt.Println("where:\n", lowIds)

	alldata := users.Select(nil, nil)
	fmt.Println("alldata:\n", alldata)

	small := users.Limit(4)
	fmt.Println("limit:\n", small)

	g := users.GroupBy(nil, Aggregators{"sumUids": sumUids}, nil)
	fmt.Println("groupby:\n", g)

	g = users.GroupBy([]string{"nfriends"}, Aggregators{"sumUids": sumUids}, nil)
	fmt.Println("groupby nfriends:\n", g)

	sorted := users.OrderBy("nfriends")
	fmt.Println("sorted:\n", sorted)

	uinterests := NewTable(
		Columns{"userID": "int", "interest": "string"},
		[]Row{
			Row{"userID": 0, "interest": "SQL"}, Row{"userID": 0, "interest": "NoSQL"},
			Row{"userID": 2, "interest": "SQL"},
		},
	)
	fmt.Println("user interests before insertion\n", uinterests)
	uinterests.Insert(Row{"userID": 2, "interest": "MySQL"})
	fmt.Println("user interests after insertion\n", uinterests)

	jtb := users.Join(uinterests, true)
	fmt.Println("join table\n", jtb)

}
