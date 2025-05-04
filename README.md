# appu

[![Coverage Status](https://coveralls.io/repos/github/EDyO/appu/badge.svg)](https://coveralls.io/github/EDyO/appu)

**A**utomatic **P**odcast **PU**blisher, aka appu, is a toolkit for podcast edition and publishing.

## Rationale

While running the [Entre Dev y Ops podcast](https://www.entredevyops.es), the authors found interesting to start building a set of tools to make this easier. We hope this might help anyone else.

Currently we start preparing every episode by writing a simple script we store in a shared Drive folder.

We record it using some videoconferencing tool, then we convert the video file to an audio track we store.

We also have an S3 bucket and CDN configured to serve the audio files and the RSS feed. After we published the audio file, we also publish a new article about it in our blog.

Finally, using the tools here, and our own podcast configuration file, we have most of this automated, so the mistakes are the less and we can publish sooner.

## Usage

### Requirements

You'll need the following:

- Docker, for Windows and Mac, you should use Docker Desktop.
- Publishing infrastructure based on an online storage, and a CDN with invalidation features (currently only AWS S3 and CloudFront are supported.)
- Valid credentials for uploading the episodes' audio files and the RSS feed and then invalidating them on the CDN.

We recommend to use some secure online storage for your podcast configuration and specific details.
It's also interesting for sharing the publishing process within teams.

While appu accepts using local files as master copies, we recommend to have them online.
HTTP/HTTPS and S3 sources are currently supported.

### Publish pipeline

The following are some environment variables you'll need to specify to have this running.

```bash
export PODCAST_YAML=/path/to/your/podcast.yaml
export DRIVE_CREDENTIALS_FILE=/path/to/your/drive_credentials.json
export AWS_PROFILE=appu
```

#### Collect data for episode

The following command creates the episode configuration file, with the publishing details for this episode calculated. The created file is named with the first part of the filename and in YAML format. In the example command, it would be named `mypodcast-XX.yaml`:


```bash
./epidator mypodcast-XX.master.mp3
```

#### Edit and upload the audio file

```bash
docker build -t ghcr.io/edyo/appu:local appu/.
docker run --rm \
	-v ${PWD}/data/cfg:/home/appu/cfg \
	-v ${HOME}/.aws/credentials:/home/appu/.aws/credentials \
	-v ${PWD}/data/files:/home/appu/files \
	-v ${PWD}/data/podcast:/home/appu/podcast \
	ghcr.io/edyo/appu:local
```

#### Download and update the feed

```bash
./feedupdater http://my.podcast.com/podcast/feed.xml mypodcast-XX.yaml > new_feed.xml
```

#### Upload the new feed

```bash
./uploader new_feed.xml feed.xml mypodcast-XX.yaml
```

First argument is the name of the XML file with the new episode entry. The second argument is the bucket key to upload the file to. The Third argument is the episode configuration file.

### Other operations

#### Extract audio from video

This converts a video file to an audio file.

```bash
ffmpeg -i recording.mp4 mypodcast-XX.master.mp3
```

#### Get audio for an episode recorded in two video files

This converts a two part video recording into a single audio file.

```bash
ffmpeg -i first_recording.mp4 mypodcast-XX.1.master.mp3
ffmpeg -i second_recording.mp4 mypodcast-XX.2.master.mp3 
ffmpeg -i "concat:mypodcast-XX.1.master.mp3|mypodcast-XX.2.master.mp3" -acodec copy mypodcast-XX.master.mp3
```

## Roadmap

So far we are planning for three versions for the toolkit:

1. current, [v0.x](https://github.com/EDyO/appu/milestone/1),
1. a more stable one, [v1.x](https://github.com/EDyO/appu/milestone/2),
1. [v2.x](https://github.com/EDyO/appu/milestone/3) with more features.
