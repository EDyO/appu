package aws

import (
	"github.com/aws/aws-sdk-go/aws"
	"github.com/aws/aws-sdk-go/aws/session"
)

// GetSession obtains a new session object to use with AWS services.
func GetSession(region string) (*session.Session, error) {
	session, err := session.NewSession(&aws.Config{Region: aws.String("eu-central-1")})
	if err != nil {
		return nil, err
	}
	return session, nil
}
