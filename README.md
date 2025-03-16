# appu

**A**utomatic **P**odcast **PU**blisher, aka appu, is a toolkit for podcast edition and publishing.

## Newer APPU 2 version

This is the new version of appu, it's a work in progress.

### Pre-requisites

Make sure you have installed in your system:

- `ffmpeg` ([download](https://www.ffmpeg.org/download.html))
- `uv` ([installation](https://docs.astral.sh/uv/getting-started/installation/))

Alternatively, you can use [APPU 2 on Docker](#use-docker-(optional)), so you'll need it.

#### Automation of `venv` management (optional)

You can use `mise` to transparently manage your venvs. Installation instructions are [here](https://mise.jdx.dev).
With `mise` installed, you just need to trust the source directory, by running `mise trust` from within the cloned repository.

#### Use Docker (optional)

You can use Docker to run APPU 2 without changing your environment.

To build the Docker image:

```bash
docker build -t appu2 .
```

To run APPU 2:

```bash
docker run --rm -v ${HOME}/mypodcast:/home/appu/mypodcast appu2 appu /home/appu/mypodcast/episode.yaml
```

To run APPU 2's tests:

```bash
docker run --rm -v ${PWD}/tests:/home/appu/tests appu2 uv run pytests /home/appu/tests
```

### Install deps

Run `uv sync` to install the python dependencies.

### Install pre-commit hook

Run `uv run pre-commit install` to install the pre-commit hook. (The first time you commit, it will take some time.)

### Run the tests

Run `uv run pytest tests` to run the tests for APPU 2, which should output something similar to the following:
```
============================= test session starts ==============================
platform linux -- Python 3.13.2, pytest-8.3.5, pluggy-1.5.0
rootdir: /home/appu
configfile: pyproject.toml
collected 7 items

tests/audio_test.py ...                                                  [ 42%]
tests/episode_test.py .                                                  [ 57%]
tests/remote_test.py ...                                                 [100%]

============================== 7 passed in 2.18s ===============================
```

### Run the app

Run `uv run appu` to run the app, or if you have done the right thing before, you might just be able to run `appu` directly with no parameters.

#### Run the MP3 episode edition with appu2

Considering you've run epidator the usual way, you can now run appu with `uv` and the episode.yaml file to get the old appu's feature:

```bash
uv run appu appu ~/mypodcast/episode.yaml
```

This is a sample of the output:

```bash
2025-03-09 03:59:18.438 | INFO     | appu2.logging:89 - Logging configured successfully
2025-03-09 03:59:18.438 | INFO     | appu2.cli:37 - debug=False
2025-03-09 03:59:18.438 | INFO     | appu2.cli:38 - Loading episode /home/user/mypodcast/episode.yaml config
2025-03-09 03:59:18.457 | INFO     | logging:1736 - [botocore.credentials] Found credentials in shared credentials file: ~/.aws/credentials
2025-03-09 03:59:18.548 | INFO     | appu2.remote:46 - Downloading s3://mypodcast-episodes-bucket/masters/episode.master.mp3 (Direct S3)
2025-03-09 03:59:23.668 | INFO     | appu2.cli:41 - Normalizing master audio
2025-03-09 03:59:29.027 | INFO     | appu2.remote:71 - Downloading https://my.podcast.com/intro.mp3?dl=0 (regular HTTP)
2025-03-09 03:59:32.527 | INFO     | appu2.remote:71 - Downloading https://my.podcast.com/cover.png?dl=1 (regular HTTP)
2025-03-09 03:59:34.378 | INFO     | appu2.cli:45 - Extract intro and outro
2025-03-09 03:59:35.170 | INFO     | appu2.cli:47 - Concatenating intro, master audio, and outro
2025-03-09 03:59:38.919 | INFO     | appu2.cli:49 - Exporting track
2025-03-09 04:00:21.976 | INFO     | appu2.cli:60 - Uploading track
2025-03-09 04:00:21.996 | INFO     | appu2.remote:18 - Uploading episode.mp3 to s3://mypodcast-episodes-bucket/podcast/episode.mp3
```

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
