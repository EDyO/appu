package main

import (
	"fmt"
	"log"
	"os"
	"strings"

	"github.com/EDyO/appu/pkg/appu"
	"gopkg.in/yaml.v2"
)

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

	outputData, err := yaml.Marshal(details)
	if err != nil {
		log.Fatal(err)
	}

	filename := fmt.Sprintf(
		"%s.yaml",
		strings.Split(trackName, ".")[0],
	)
	err = os.WriteFile(filename, outputData, 0644)
	if err != nil {
		log.Fatalf("Error writing yaml file: %v", err)
	}

	cfg, err := appu.LoadConfigYAML(filename)
	if err != nil {
		log.Fatalf("Error loading config file: %v", err)
	}

	cwd, err := os.Getwd()
	if err != nil {
		log.Fatal(err)
	}

	volumes := map[string]string{
		fmt.Sprintf("%s/data/aws", cwd):     "/home/appu/.aws",
		fmt.Sprintf("%s/data/cfg", cwd):     "/home/appu/cfg",
		fmt.Sprintf("%s/data/files", cwd):   "/home/appu/files",
		fmt.Sprintf("%s/data/podcast", cwd): "/home/appu/podcast",
	}

	if err := os.Mkdir(fmt.Sprintf("%s/data", cwd), 0755); err != nil {
		log.Fatal(err)
	}
	for directory := range volumes {
		if err := os.Mkdir(directory, 0755); err != nil {
			log.Fatal(err)
		}
	}

	err = cfg.PrepareFiles()
	if err != nil {
		log.Fatalf("Config error: %v", err)
	}

}
