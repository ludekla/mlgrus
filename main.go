package main

import (
    "fmt"
    "os"
    "image"
    "image/color"
    "flag"

    "mlgrus/pkg/cluster"
    "mlgrus/pkg/utils"
)

var k = flag.Int("k", 3, "number of clusters")

func transformImage(km *cluster.KMeans, img image.Image) image.Image {
	if km.Means == nil {
		panic("Please first train the k-means engine!")
	}
	size := img.Bounds().Size()
	height, width := size.X, size.Y
	newImg := image.NewRGBA64(image.Rect(0, 0, size.X, size.Y))
	for x := 0; x < height; x++ {
		for y := 0; y < width; y++ {
			r, g, b, a := img.At(x, y).RGBA()
			pt := utils.Point{float64(r), float64(g), float64(b)}
			clusterID := km.Classify(pt)
			pixel := km.Means[clusterID]
			colour := color.RGBA64{
				uint16(pixel[0]), uint16(pixel[1]), uint16(pixel[2]), uint16(a),
			}
			newImg.SetRGBA64(x, y, colour)
		}
	}
	return newImg
}

func main() {

    flag.Parse()

	img, err := utils.LoadImage("data/pics/lutz.jpg")
    if err != nil {
        fmt.Printf("Cannot load image file: %v", err)
        os.Exit(1)
    }

	pixels := utils.GetPixelData(img)

    fmt.Println(*k, len(pixels))

	km := cluster.NewKMeans(*k)
	e := km.Fit(pixels)
	fmt.Printf("%v %v\n", e, km.Means)

	newImg := transformImage(km, img)
    utils.SaveImage(newImg, fmt.Sprintf("data/pics/lutz_%d.jpg", *k))

}
