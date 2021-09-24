package main

import (
	"fmt"
	"log"
	"os"

	"github.com/EDyO/appu/pkg/aws"
)

func main() {
	uploadFileName := os.Args[1]
	bucket := os.Args[2]
	destinationKey := os.Args[3]
	distribution := os.Args[4]

	session, err := aws.GetSession("eu-central-1")
	if err != nil {
		log.Fatal(err)
	}

	if err = aws.UploadFile(session, uploadFileName, bucket, destinationKey); err != nil {
		log.Fatal(err)
	}

	pattern := fmt.Sprintf("/%s", destinationKey)
	if err := aws.CreateInvalidationRequest(session, distribution, pattern); err != nil {
		log.Fatal(err)
		return
	}
}
