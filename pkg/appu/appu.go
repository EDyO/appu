package appu

import (
	"io"
	"net/http"
	"os"
	"strings"
)

// DownloadFile allows to download a URL content into a file.
var DownloadFile = func(URL, fileName string) error {
	file, err := os.Create(fileName)
	if err != nil {
		return err
	}

	resp, err := http.Get(URL)
	if err != nil {
		return err
	}
	defer resp.Body.Close()

	_, err = io.Copy(file, resp.Body)
	if err != nil {
		return err
	}
	defer file.Close()

	return nil
}

// GetEpisodeLength returns the Content-Length HTTP header value for a URL.
var GetEpisodeLength = func(URL string) (int, error) {
	res, err := http.Head(URL)
	if err != nil {
		return 0, err
	}

	return int(res.ContentLength), nil
}

func extractFileNameFromURL(URL string) string {
	URLPathParts := strings.Split(URL, "/")
	return strings.Split(URLPathParts[len(URLPathParts)-1], "?")[0]
}
