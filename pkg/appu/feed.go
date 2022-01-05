package appu

import (
	"fmt"
	"time"

	"github.com/beevik/etree"
)

// ReadXML loads XML from a file into an `etree.Document` for processing.
func ReadXML(feedFileName string) (*etree.Document, error) {
	doc := etree.NewDocument()
	err := doc.ReadFromFile(feedFileName)
	if err != nil {
		return nil, err
	}

	return doc, err
}

// CreateFeedItem creates a new feed's Item from the Config information.
func CreateFeedItem(cfg *Config) (*etree.Element, error) {
	length, err := GetEpisodeLength(cfg.EpisodeURL)
	if err != nil {
		return nil, err
	}

	newEpisodeTag := etree.NewElement("item")

	title := etree.NewElement("title")
	title.CreateText(cfg.Title)
	newEpisodeTag.AddChild(title)

	link := etree.NewElement("link")
	link.CreateText(cfg.EpisodeURL)
	newEpisodeTag.AddChild(link)

	guid := etree.NewElement("guid")
	guid.CreateText(cfg.EpisodeURL)
	newEpisodeTag.AddChild(guid)

	description := etree.NewElement("description")
	descriptionText := cfg.Summary + "\n"
	for _, link := range cfg.Links {
		descriptionText += link + "\n"
	}
	description.CreateText(descriptionText)
	newEpisodeTag.AddChild(description)

	pubDate := etree.NewElement("pubDate")
	pubDate.CreateText(cfg.PubDate.Format(time.RFC1123Z))
	newEpisodeTag.AddChild(pubDate)

	enclosure := etree.NewElement("enclosure")
	enclosure.CreateAttr("length", fmt.Sprintf("%v", length))
	enclosure.CreateAttr("type", "audio/mpeg")
	enclosure.CreateAttr("url", cfg.EpisodeURL)

	newEpisodeTag.AddChild(enclosure)

	return newEpisodeTag, nil
}

// WriteXML creates a new file on disk with the appropriate XML contents from `doc`.
func WriteXML(doc *etree.Document) {
	doc.Indent(2)
	doc.WriteToFile("new_feed.xml")
}
