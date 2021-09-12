package main

import (
	"fmt"
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
	AWSCredentialsFileName := os.Args[3]

	cfg, err := appu.LoadConfigYAML(YAMLFileName)
	if err != nil {
		log.Fatalf("Error loading config file: %v", err)
	}

	err = cfg.PrepareFiles()
	if err != nil {
		log.Fatalf("Config error: %v", err)
	}

	cwd, err := os.Getwd()
	if err != nil {
		log.Fatal(err)
	}
	volumes := map[string]string{
		AWSCredentialsFileName:                        "/home/appu/.aws/credentials",
		fmt.Sprintf("%s/%s", cwd, cfg.ConfigFileName): "/home/appu/config.cfg",
		fmt.Sprintf("%s/%s", cwd, cfg.CoverFileName):  fmt.Sprintf("/home/appu/files/%s", cfg.CoverFileName),
	}

	out, err := docker.RunAppuContainer(DockerImage, volumes)
	if err != nil {
		log.Fatal(err)
	}

	stdcopy.StdCopy(os.Stdout, os.Stderr, out)
}
