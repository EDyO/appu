# APPu

APPu, **A**utomatic **P**odcast **Pu**blisher, is a tool used to automate podcast episodes' publishing, as we do at the [EDyO](http://www.entredevyops.es) podcast.


## Description

This tool:

1. Downloads the media to edit the audio track: The master recording, and the intro and outro.
2. Joins these tracks and normalizes the volume.
3. Fills the ID3 tags, including the cover image, from provided information.
4. Uploads the resulting audio track to the specified bucket.

The information required is provided through a configuration file.

## Requirements

You'll need:
* to have either [Docker](https://docs.docker.com/get-docker/), for Linux, Mac or Windows, installed, and
* credentials to store the edited audio track in the publishing bucket.

## Usage
### How to build it

1. Clone the git repository and jump into it, 
    ```
    git clone https://github.com/EDyO/appu.git
    cd appu
    ```
    
    or jump into it and pull the latest changes:
    ```
    cd appu
    git pull
    ```

2. Build the image:
    ```
    docker build --pull --rm -f "Dockerfile" -t appu .
    ```

### How to use it

1. Create your `config.cfg`:

   This is an [INI](https://docs.python.org/3/library/configparser.html#supported-ini-file-structure) file, with the following sections and keys:
   * In the `files-config`:
     * `podcast_file`: A path or URL pointing to the master recording.
     * `song_file`: A path or URL to the intro and outro jingles. The program will use the first second of the song as intro, and the last 4 seconds, as the outro.
     * `cover_file`: A path to the image to use as cover in the resulting audio track.
     * `final_file`: The bucket object ID.
     * `podcast_bucket`: The name of the publishing bucket.
   * In the `tag-config`:
     * `title`: The title of the episode.
     * `artist`: The name of the author/s.
     * `album`: The name of the podcast.
     * `track`: The number of this track.
     * `year`: The year of the publishing.
     * `comment`: The summary of the episode.

2. Run the appu container. The following is an example of the run command in Linux:
   ```
   docker run --rm -v $(pwd)/yourconfig.cfg:/home/appu/config.cfg -v $(pwd)/bucket.credentials:/home/appu/.aws/credentials appu
   ```
   
On completion, your episode should be present in the specified bucket.