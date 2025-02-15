package appu

import (
	"fmt"
	"os"
	"strings"
	"time"

	"gopkg.in/ini.v1"
	"gopkg.in/yaml.v2"
)

// Config contains all the configuration data from the YAML file.
// Part of it is used by the appu container.
type Config struct {
	Album          string `yaml:"album"`
	Artist         string `yaml:"artist"`
	Bucket         string `yaml:"bucket"`
	Cover          string `yaml:"cover"`
	CoverFileName  string
	Image          string    `yaml:"image"`
	Intro          string    `yaml:"intro"`
	Links          []string  `yaml:"links"`
	Master         string    `yaml:"master"`
	PubDate        time.Time `yaml:"pubDate"`
	Summary        string    `yaml:"summary"`
	Title          string    `yaml:"title"`
	TrackNo        int       `yaml:"trackNo"`
	EpisodeURL     string    `yaml:"episodeURL"`
	DistributionID string    `yaml:"distributionID"`
	ConfigFileName string
}

// LoadConfigYAML reads the `YAMLFile` and gets the data loaded in
// `cfg`, or any error happened in the process.
func LoadConfigYAML(YAMLFile string) (cfg *Config, err error) {
	yamlFile, err := os.ReadFile(YAMLFile)
	if err != nil {
		return nil, fmt.Errorf(
			"error loading %s: %v ",
			YAMLFile,
			err,
		)
	}

	err = yaml.Unmarshal(yamlFile, &cfg)
	if err != nil {
		return nil, fmt.Errorf(
			"error unmarshaling %s: %v",
			YAMLFile,
			err,
		)
	}

	return cfg, nil
}

// PrepareFiles makes all the configuration ready to be used by the
// appu container.
func (c *Config) PrepareFiles() (err error) {
	c.CoverFileName = extractFileNameFromURL(c.Cover)
	c.ConfigFileName = "data/cfg/config.cfg"

	err = DownloadFile(
		c.Cover,
		fmt.Sprintf("data/files/%s", c.CoverFileName),
	)
	if err != nil {
		return fmt.Errorf("error downloading cover file: %v", err)
	}

	c.createConfigFile(c.ConfigFileName)

	return nil
}

func (c *Config) createConfigFile(configFileName string) {
	cfgINI := ini.Empty()
	filesSection := cfgINI.Section("files-config")
	filesSection.Key("podcast_file").SetValue(c.Master)
	filesSection.Key("song_file").SetValue(c.Intro)
	filesSection.Key("cover_file").SetValue(fmt.Sprintf(
		"files/%s",
		c.CoverFileName,
	))
	filesSection.Key("final_file").SetValue(fmt.Sprintf(
		"podcast/%s",
		c.episodeName(),
	))
	filesSection.Key("podcast_bucket").SetValue(c.Bucket)
	tagSection := cfgINI.Section("tag-config")
	tagSection.Key("title").SetValue(c.Title)
	tagSection.Key("artist").SetValue(c.Artist)
	tagSection.Key("album").SetValue(c.Album)
	tagSection.Key("track").SetValue(fmt.Sprintf(
		"%d",
		c.TrackNo,
	))
	tagSection.Key("year").SetValue(fmt.Sprintf(
		"%d",
		c.year(),
	))
	tagSection.Key("comment").SetValue(c.Summary)
	cfgINI.SaveTo(configFileName)
}

func (c *Config) episodeName() string {
	return strings.Replace(
		extractFileNameFromURL(c.Master),
		".master",
		"",
		1,
	)
}

func (c *Config) year() int {
	return c.PubDate.Year()
}
