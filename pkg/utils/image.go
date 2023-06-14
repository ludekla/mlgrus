package utils

import (
	"fmt"
	"image"
	"image/jpeg"
	"os"
)

func LoadImage(filename string) (image.Image, error) {
	var img image.Image
	imgfile, err := os.Open(filename)
	if err != nil {
		return img, fmt.Errorf("cannot open picture: %v", err)
	}
	defer imgfile.Close()
	img, err = jpeg.Decode(imgfile)
	if err != nil {
		return img, fmt.Errorf("cannot decode the file: %v", err)
	}
	return img, nil
}

func GetPixelData(img image.Image) []Point {
	size := img.Bounds().Size()
	width, height := size.X, size.Y
	pixels := make([]Point, width*height)
	for x := 0; x < height; x++ {
		for y := 0; y < width; y++ {
			r, g, b, _ := img.At(x, y).RGBA()
			pixels[x*width+y] = Point{float64(r), float64(g), float64(b)}
		}
	}
	return pixels
}

func SaveImage(img image.Image, filepath string) error {
	outFile, err := os.Create(filepath)
	if err != nil {
		return fmt.Errorf("cannot create image file: %v", err)
	}
	defer outFile.Close()
	return jpeg.Encode(outFile, img, nil)
}
