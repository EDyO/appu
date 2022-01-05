package main

import (
	"fmt"
	"io/ioutil"
	"log"
	"os"

	"github.com/EDyO/appu/pkg/appu"
	"github.com/EDyO/appu/pkg/docker"
	"github.com/docker/docker/pkg/stdcopy"
)

func main() {
	log.SetFlags(0)

	YAMLFileName := os.Args[1]
	DockerImage := os.Args[2]
	AWSCredentials := os.Args[3]

	cfg, err := appu.LoadConfigYAML(YAMLFileName)
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

	input, err := ioutil.ReadFile(AWSCredentials)
	if err != nil {
		fmt.Println(err)
		return
	}

	destinationFile := fmt.Sprintf("%s/data/aws/credentials", cwd)
	err = ioutil.WriteFile(destinationFile, input, 0644)
	if err != nil {
		fmt.Println("Error creating", destinationFile)
		fmt.Println(err)
		return
	}

	out, err := docker.RunAppuContainer(DockerImage, volumes)
	if err != nil {
		log.Fatal(err)
	}

	stdcopy.StdCopy(os.Stdout, os.Stderr, out)

	if err := os.RemoveAll(fmt.Sprintf("%s/data", cwd)); err != nil {
		log.Fatal(err)
	}
}
