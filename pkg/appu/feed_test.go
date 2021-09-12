package appu

import (
	"testing"
	"time"
)

func MockGetEpisodeLength(length int, err error) func(string) (int, error) {
	return func(string) (int, error) {
		if err != nil {
			return 0, err
		}
		return length, nil
	}
}

func TestCreateFeedItem(t *testing.T) {
	FakeDate, err := time.Parse("2006-01-02T15:04:05.999999999Z07:00", "2021-09-10T17:21:37.771516069+02:00")
	if err != nil {
		t.Errorf("Error parsing fake date: %v", err)
	}
	GetEpisodeLength = MockGetEpisodeLength(1900000, nil)

	tcs := []struct {
		Config                                                                 *Config
		Title, Link, GUID, Description, PubDate, EnclosureLength, EnclosureURL string
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
				Master:     "https://my.podcast.com/masters/mypodcast-1.master.mp3",
				PubDate:    FakeDate,
				Summary:    "In this episode I'll talk about my podcast.",
				Title:      "Podcast 1 - My Podcast",
				TrackNo:    1,
				EpisodeURL: "https://my.podcast.com/podcast/mypodcast-1.mp3",
			},
			"Podcast 1 - My Podcast",
			"https://my.podcast.com/podcast/mypodcast-1.mp3",
			"https://my.podcast.com/podcast/mypodcast-1.mp3",
			"In this episode I'll talk about my podcast.",
			FakeDate.Format(time.RFC1123Z),
			"1900000",
			"https://my.podcast.com/podcast/mypodcast-1.mp3",
		},
	}

	for _, tc := range tcs {
		newEpisodeTag, err := CreateFeedItem(tc.Config)
		if err != nil {
			t.Errorf("Unexpected error creating feed item: %v", err)
		}

		if newEpisodeTag.Tag != "item" {
			t.Errorf("wrong tag '%s', expected 'item'", newEpisodeTag.Tag)
		}
	}
}
