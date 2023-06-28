package appu

import (
	"fmt"
	"os"
	"strconv"
	"time"

	"github.com/beevik/etree"
	"github.com/eduncan911/podcast"
	"github.com/mmcdole/gofeed"
)

// AddNewEpisode creates a new episode from `cfg` and adds it to `feed`.
func AddNewEpisode(cfg *Config, feed *podcast.Podcast) error {
	description := cfg.Summary + "\n"
	for _, link := range cfg.Links {
		description += link + "\n"
	}
	newItem := podcast.Item{
		Title:       cfg.Title,
		Description: description,
		PubDate:     &cfg.PubDate,
	}
	length, err := GetEpisodeLength(cfg.EpisodeURL)
	if err != nil {
		return err
	}
	newItem.AddEnclosure(cfg.EpisodeURL, podcast.MP3, int64(length))

	if _, err := feed.AddItem(newItem); err != nil {
		return err
	}

	return nil
}

// ReadXML loads XML from a file into a `podcast.Podcast` for processing.
func ReadXML(cfg *Config, feedFileName string) (*podcast.Podcast, error) {
	file, err := os.Open(feedFileName)
	if err != nil {
		return nil, err
	}
	defer file.Close()

	fp := gofeed.NewParser()
	feed, err := fp.Parse(file)
	if err != nil {
		return nil, err
	}

	p := podcast.New(
		feed.Title,
		feed.Link,
		feed.Description,
		&cfg.PubDate,
		&cfg.PubDate,
	)

	p.AddAtomLink(feed.Link)
	p.ISubtitle = feed.ITunesExt.Subtitle
	p.AddAuthor(feed.ITunesExt.Author, feed.ITunesExt.Owner.Email)
	p.AddImage(feed.ITunesExt.Image)
	p.AddSummary(feed.ITunesExt.Summary)
	for _, category := range feed.ITunesExt.Categories {
		p.AddCategory(category.Text, nil)
	}
	p.IOwner = &podcast.Author{
		Name:  feed.ITunesExt.Owner.Name,
		Email: feed.ITunesExt.Owner.Email,
	}
	p.IExplicit = feed.ITunesExt.Explicit
	p.Language = feed.Language
	p.Copyright = feed.Copyright

	for _, item := range feed.Items {
		podcastItem := podcast.Item{
			Title:       item.Title,
			Description: item.Description,
			PubDate:     item.PublishedParsed,
		}
		for _, itemEnclosure := range item.Enclosures {
			length, err := strconv.ParseInt(itemEnclosure.Length, 10, 64)
			if err != nil {
				return nil, err
			}
			podcastItem.AddEnclosure(itemEnclosure.URL, podcast.MP3, length)
		}
		if _, err := p.AddItem(podcastItem); err != nil {
			return nil, err
		}
	}

	return &p, nil
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
func WriteXML(p *podcast.Podcast) {

	// Podcast.Encode writes to an io.Writer
	if err := p.Encode(os.Stdout); err != nil {
		fmt.Println("error writing to stdout:", err.Error())
	}
}
