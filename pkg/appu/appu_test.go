package appu

import (
	"testing"
)

func TestExtractFileNameFromURL(t *testing.T) {
	tcs := []struct {
		URL              string
		expectedFileName string
	}{
		{
			URL:              "https://cloudstorage.example.com/file.png",
			expectedFileName: "file.png",
		},
		{
			URL:              "https://cloudstorage.example.com/file.png?some-param=some-value",
			expectedFileName: "file.png",
		},
	}

	for _, tc := range tcs {
		fileName := extractFileNameFromURL(tc.URL)

		if fileName != tc.expectedFileName {
			t.Errorf("wrong file name '%s', expected '%s'", fileName, tc.expectedFileName)
		}
	}
}
