package main

import (
	"bytes"
	"fmt"
	"log"
	"net/http"
	"os"
	"time"

	"github.com/aws/aws-sdk-go/aws"
	"github.com/aws/aws-sdk-go/aws/session"
	"github.com/aws/aws-sdk-go/service/cloudfront"
	"github.com/aws/aws-sdk-go/service/s3"
)

func uploadFile(session *session.Session, uploadFileDir, bucket, destinationKey string) error {
	upFile, err := os.Open(uploadFileDir)
	if err != nil {
		return err
	}
	defer upFile.Close()

	upFileInfo, _ := upFile.Stat()
	var fileSize int64 = upFileInfo.Size()
	fileBuffer := make([]byte, fileSize)
	upFile.Read(fileBuffer)

	_, err = s3.New(session).PutObject(&s3.PutObjectInput{
		Bucket:               aws.String(bucket),
		Key:                  aws.String(destinationKey),
		ACL:                  aws.String("private"),
		Body:                 bytes.NewReader(fileBuffer),
		ContentLength:        aws.Int64(fileSize),
		ContentType:          aws.String(http.DetectContentType(fileBuffer)),
		ContentDisposition:   aws.String("attachment"),
		ServerSideEncryption: aws.String("AES256"),
	})
	return err
}

func createInvalidationRequest(session *session.Session, distribution, pattern string) error {
	_, err := cloudfront.New(session).CreateInvalidation(&cloudfront.CreateInvalidationInput{
		DistributionId: aws.String(distribution),
		InvalidationBatch: &cloudfront.InvalidationBatch{
			CallerReference: aws.String(
				fmt.Sprintf("appu-%s", time.Now().Format("2006/01/02,15:04:05"))),
			Paths: &cloudfront.Paths{
				Quantity: aws.Int64(1),
				Items: []*string{
					aws.String(pattern),
				},
			},
		},
	})
	if err != nil {
		return fmt.Errorf("error creating invalidation:%v", err.Error())
	}

	return nil
}

func main() {
	uploadFileName := os.Args[1]
	bucket := os.Args[2]
	destinationKey := os.Args[3]
	distribution := os.Args[4]

	session, err := session.NewSession(&aws.Config{Region: aws.String("eu-central-1")})
	if err != nil {
		log.Fatal(err)
	}

	if err = uploadFile(session, uploadFileName, bucket, destinationKey); err != nil {
		log.Fatal(err)
	}

	pattern := fmt.Sprintf("/%s", destinationKey)
	if err := createInvalidationRequest(session, distribution, pattern); err != nil {
		log.Fatal(err)
		return
	}
}
