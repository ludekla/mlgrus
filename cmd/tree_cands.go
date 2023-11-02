package main

import (
	"fmt"

	"mlgrus/pkg/tree"
)

func main() {

	cands := tree.FromCSV("data/csv/cands.csv")
	data := make([]interface{}, len(cands))
	for i, cand := range cands {
		data[i] = cand.Get("phd")
	}
	x := tree.DataEntropy(data)
	fmt.Printf("%v\n", x)

	p := tree.PartitionBy(cands, "phd")
	q := tree.PartitionBy(cands, "lang")

	fmt.Printf("phd partition by phd %v\n", tree.PartitionEntropyBy(p, "phd"))
	fmt.Printf("phd partition by lang %v\n", tree.PartitionEntropyBy(p, "lang"))

	fmt.Printf("lang partition by phd %v\n", tree.PartitionEntropyBy(q, "phd"))
	fmt.Printf("lang partition by lang %v\n", tree.PartitionEntropyBy(q, "lang"))

	t := tree.New(
		"level",
		false,
		tree.Branches{
			"Junior": tree.New(
				"phd",
				false,
				tree.Branches{
					true:  tree.New("", false, nil), // leaves
					false: tree.New("", true, nil),
				},
			),
			"Mid": tree.New("", true, nil),
			"Senior": tree.New(
				"tweets",
				false,
				tree.Branches{
					true:  tree.New("", true, nil),
					false: tree.New("", false, nil),
				},
			),
		},
	)

	for _, cand := range cands {
		fmt.Printf("hire?: %v - %v\n", cand.Get("didwell"), t.Classify(cand))
	}

	fmt.Println("learned tree")

	mt := tree.BuildTree(cands, []string{"level", "lang", "tweets", "phd"}, "didwell")
	for _, cand := range cands {
		fmt.Printf("hire?: %v - %v\n", cand.Get("didwell"), mt.Classify(cand))
	}

	c := tree.Candidate{Level: "Intern", Lang: "Java", Tweets: true, PhD: true, DidWell: false}
	ans := t.Classify(&c)
	fmt.Printf("Hire?: handcrafted tree says %v\n", ans)
	ans = mt.Classify(&c)
	fmt.Printf("Hire?: trained tree says %v\n", ans)
}
