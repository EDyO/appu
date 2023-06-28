package main

import (
	"log"
	"os"

	"github.com/EDyO/appu/pkg/appu"
)

func main() {
	log.SetFlags(0)

	feedURL := os.Args[1]
	YAMLFileName := os.Args[2]
	feedFileName := "feed_podcast.xml"

	cfg, err := appu.LoadConfigYAML(YAMLFileName)
	if err != nil {
		log.Fatalf("Error loading config file: %v", err)
	}

	err = appu.DownloadFile(feedURL, feedFileName)
	if err != nil {
		log.Fatalf("Error downloading feed %s: %v", feedURL, err)
	}

	feed, err := appu.ReadXML(cfg, feedFileName)
	if err != nil {
		log.Fatalf("Error parsing feed: %v", err)
	}

	err = appu.AddNewEpisode(cfg, feed)
	if err != nil {
		log.Fatalf("Error adding new episode: %v", err)
	}

	appu.WriteXML(feed)
}
