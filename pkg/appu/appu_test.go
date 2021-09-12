package appu

import (
	"os"
	"testing"
	"time"
)

func MockDownload() func(string, string) error {
	return func(string, string) error {
		return nil
	}
}

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

func TestConfig(t *testing.T) {
	FakeDate, err := time.Parse("2006-01-02T15:04:05.999999999Z07:00", "2021-09-10T17:21:37.771516069+02:00")
	if err != nil {
		t.Errorf("Error parsing fake date: %v", err)
	}
	DownloadFile = MockDownload()

	tcs := []struct {
		Config             *Config
		expectedConfigFile string
	}{
		{
			&Config{
				Album:  "My Podcast",
				Artist: "Me",
				Bucket: "mypodcast-episodes",
				Cover:  "https://my.podcast.com/media/cover.png",
				Image:  "https://my.podcast.com/images/image.png",
				Intro:  "https://my.podcast.com/media/intro.mp3",
				Links: []string{
					"One mentioned link - https://my.podcast.com/referrals",
				},
				Master:  "https://my.podcast.com/masters/mypodcast-1.master.mp3",
				PubDate: FakeDate,
				Summary: "In this episode I'll talk about my podcast.",
				Title:   "Podcast 1 - My Podcast",
				TrackNo: 1,
			},
			"../../test_data/fixture.cfg",
		},
	}

	for _, tc := range tcs {
		expectedConfig, err := os.ReadFile(tc.expectedConfigFile)
		if err != nil {
			t.Errorf("Unexpected error loading fixture config: %v", err)
		}
		expectedConfigContents := string(expectedConfig)

		err = tc.Config.PrepareFiles()
		if err != nil {
			t.Errorf("Unexpected error: %v", err)
		}

		configFile, err := os.ReadFile("config.cfg")
		if err != nil {
			t.Errorf("Unexpected error reading config file: %v", err)
		}

		configFileContents := string(configFile)
		if configFileContents != expectedConfigContents {
			t.Errorf("Expected configuration contents are not matching: \ngot \n'%v'expected \n'%v'", configFileContents, expectedConfigContents)
		}
	}
}
