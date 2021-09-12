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

	doc, err := appu.ReadXML(feedFileName)
	if err != nil {
		log.Fatalf("Error parsing feed: %v", err)
	}

	channel := doc.FindElement("./rss/channel")
	if channel != nil {
		newEpisodeTag, err := appu.CreateFeedItem(cfg)
		if err != nil {
			log.Fatalf("Error creating new episode tag: %v", err)
		}
		channel.AddChild(newEpisodeTag)
	} else {
		log.Fatalf("Error: could not find channel tagin feed XML")
	}

	appu.WriteXML(doc)
}
