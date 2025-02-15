package appu

// GetEpisodeDetails provides the corresponding episode details for
// the `trackName` provided according to the features defined in
// `podcastYAML`.
func GetEpisodeDetails(trackName, podcastYAML string) (
	map[string]interface{},
	error,
) {
	podcast, err := NewPodcast(trackName, podcastYAML)
	if err != nil {
		return nil, err
	}

	return podcast.details, nil
}
