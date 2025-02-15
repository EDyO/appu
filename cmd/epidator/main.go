package main

import (
	"fmt"
	"log"
	"os"

	"github.com/EDyO/appu/pkg/appu"
	"gopkg.in/yaml.v2"
)

func printYAML(properties map[string]interface{}) error {
	outputData, err := yaml.Marshal(properties)
	if err != nil {
		return err
	}

	fmt.Println(string(outputData))
	return nil
}

func main() {
	log.SetFlags(0)

	trackName := os.Args[1]
	podcastYAML := os.Getenv("PODCAST_YAML")
	if podcastYAML == "" {
		podcastYAML = "podcast.yaml"
	}

	details, err := appu.GetEpisodeDetails(
		trackName,
		podcastYAML,
	)
	if err != nil {
		log.Fatal(err)
	}

	printYAML(details)
}
