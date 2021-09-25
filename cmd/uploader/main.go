package main

import (
	"fmt"
	"log"
	"os"

	"github.com/EDyO/appu/pkg/appu"
	"github.com/EDyO/appu/pkg/aws"
)

func main() {
	uploadFileName := os.Args[1]
	distribution := os.Args[4]
	destinationKey := os.Args[2]
	YAMLFileName := os.Args[3]

	cfg, err := appu.LoadConfigYAML(YAMLFileName)
	if err != nil {
		log.Fatalf("Error loading config file: %v", err)
	}

	session, err := aws.GetSession("eu-central-1")
	if err != nil {
		log.Fatal(err)
	}

	if err = aws.UploadFile(session, uploadFileName, cfg.Bucket, destinationKey); err != nil {
		log.Fatal(err)
	}

	pattern := fmt.Sprintf("/%s", destinationKey)
	if err := aws.CreateInvalidationRequest(session, distribution, pattern); err != nil {
		log.Fatal(err)
		return
	}
}
