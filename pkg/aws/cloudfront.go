package aws

import (
	"fmt"
	"time"

	"github.com/aws/aws-sdk-go/aws"
	"github.com/aws/aws-sdk-go/aws/session"
	"github.com/aws/aws-sdk-go/service/cloudfront"
)

// CreateInvalidationRequest created a new Invalidation request for `distribution` on `pattern`, using `session` provided.
func CreateInvalidationRequest(session *session.Session, distribution, pattern string) error {
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
