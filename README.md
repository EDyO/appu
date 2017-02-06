# APPU
**A**utomatic **P**odcast **Pu**blisher

Python tool used to automate the [EDyO](http://www.entredevyops.es) podcast publication.

How it works
------------

* Clone the git repo

> ``` git clone https://github.com/dacacioa/AAE.git ```

* Put in the folder files:

  * The main podcast audio files.
  * The intro/ending music.
  * The podcast's cover image.

** IMPORTANT: the files must be in mp3 format.**

* Modify config.cfg file setting:

  * [files-config] section:

    * podcast_file --> The main podcast audio files (f.e files/main.mp3).
    * song_file --> Intro/ending song file.
    * cover_file --> The cover image file.
    * final_file --> The final result file. It will be stored in podcast folder (f.e. podscat/EDyO-20.mp3).

  * [tag-config] section is the id3 metadata to add to the file. You have to set it without simple/double quotation marks.

* Finally, you have to push into Github master repo branch.

> ``` git push https://github.com/dacacioa/AAE.git origing/master ```

Then Travis CI will take the repo and will generate a new branch (travis-ci) with the final file set in the final_file param.
You will can download it directly from Github.
