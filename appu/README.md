# 🎧 APPu

APPu, **A**utomatic **P**odcast **Pu**blisher, is a tool used to automate podcast episodes' publishing, as we do at the [EDyO](http://www.entredevyops.es) podcast.

## 📖 Description

This tool automates the podcast episode publication workflow:

1. **⬇️ Downloads and merges audio**: Retrieves the master recording, intro, and outro tracks from local paths or remote URLs (HTTP/HTTPS or S3).
2. **🎛️ Processes audio**: Joins tracks together, normalizes volume levels, y recorta silencios largos de forma suave.
3. **📝 Embeds metadata**: Fills ID3 tags with episode information and embeds cover artwork.
4. **☁️ Optionally uploads**: Publishes the final audio file to an S3 bucket (can be skipped with `--no-upload` flag).

All configuration is managed through a single INI-format `config.cfg` file.

## ✅ Requirements

You'll need:
* 🐍 Python 3.7+
* 📦 Dependencies listed in `requirements.txt` (installed automatically in Docker)
* 🔑 AWS credentials (if uploading to S3)
* 🐳 [Optional] Docker for containerized execution

**Supported Audio Sources:**
- 📁 Local files
- 🌐 HTTP/HTTPS URLs
- ☁️ S3 URLs (requires AWS credentials)

## 🚀 Usage

### ⚡ Quick Start (Python)

1. **Create a `config.cfg`** file (see Configuration section below)

2. **Run directly with Python:**
   ```bash
   # From the project root
   python appu/appu.py
   
   # Or from the appu directory
   cd appu && python appu.py
   ```

3. **Skip S3 upload** (generate file locally only):
   ```bash
   python appu/appu.py --no-upload
   ```

4. **Enable debug output:**
   ```bash
   python appu/appu.py -debug
   ```

### 🐳 Docker Usage

1. Build the image:
   ```bash
   docker build --pull --rm -f "Dockerfile" -t appu .
   ```

2. Run the container:
   ```bash
   docker run --rm \
     -v $(pwd)/config.cfg:/home/appu/cfg/config.cfg \
     -v $(pwd)/.aws/credentials:/home/appu/.aws/credentials \
     appu
   ```

   To skip S3 upload:
   ```bash
   docker run --rm \
     -v $(pwd)/config.cfg:/home/appu/cfg/config.cfg \
     appu \
     python appu.py --no-upload
   ```

## ⚙️ Configuration

Create a `config.cfg` file in INI format with the following sections:

### 📂 `[files-config]` Section

| Key | Description | Example |
|-----|-------------|---------|
| `podcast_file` | URL or path to master recording (HTTP/HTTPS or S3) | `https://cdn.example.com/podcast.mp3` |
| `song_file` | URL or path to jingles (first 1s = intro, last 4s = outro) | `files/intro.mp3` |
| `cover_file` | Path to cover artwork image | `files/cover.png` |
| `final_file` | Output filename for final episode | `podcast/episode-001.mp3` |
| `podcast_bucket` | S3 bucket name (leave empty to skip upload) | `my-podcast-episodes` |

### 🏷️ `[tag-config]` Section

| Key | Description | Example |
|-----|-------------|---------|
| `title` | Episode title | `Episode 001 - My Podcast` |
| `artist` | Author/host name(s) | `John Doe` |
| `album` | Podcast name | `My Podcast` |
| `track` | Episode number | `1` |
| `year` | Publication year | `2026` |
| `comment` | Episode summary/description | `In this episode we discuss...` |

### Example Configuration

```ini
[files-config]
podcast_file   = https://cdn.example.com/masters/episode-001.master.mp3
song_file      = files/intro.mp3
cover_file     = files/cover.png
final_file     = podcast/episode-001.mp3
podcast_bucket = my-podcast-episodes

[tag-config]
title   = Episode 001 - My Podcast
artist  = John Doe
album   = My Podcast
track   = 1
year    = 2026
comment = A great episode about podcasting.
```

## 🎛️ Flags & Options

- **`--no-upload`**: Generate the final audio file without uploading to S3. Useful for testing or local publishing.
- **`-debug`**: Enable debug logging for troubleshooting.

## 🔊 Audio Processing Defaults

- **Recorte de silencios**: detecta tramos muy silenciosos con un umbral de `audio.dBFS - 25` (mínimo -65 dB) para evitar cortar finales de frase en voz baja.
- **Longitud máxima de silencio**: los silencios se recortan a **900 ms**, conservando **200 ms** en cada borde para mantener respiraciones y colas naturales.
- **Suavizado**: se aplican fades de **30 ms** en los bordes, sin solape, para evitar cortes bruscos.
- **Silencio de cola**: se añaden **4 s** de silencio al final del audio exportado (se aplica después de normalizar y recortar silencios).
- **Crossfades ajustados**: entrada del podcast con **800 ms** de crossfade para que la intro no se corte en seco, y entrada del outro con **500 ms** para evitar que el jingle tape los últimos segundos.
- **Headroom y compresión suave**: se normaliza a **-3 dBFS** y se aplica compresión ligera (umbral -18 dB, ratio 3:1, attack 5 ms, release 120 ms) para evitar crepitaciones por saturación sin aplastar la dinámica.

> Si necesitas ajustar la sensibilidad o la duración de las pausas, modifica los valores por defecto de `clamp_silence` y `add_tail_silence` en `appu/audio.py` (parámetros `max_silence_ms`, `edge_keep_ms`, `crossfade_ms` y `silence_thresh`).

## ✨ Recent Features

### 🆕 New in Latest Version

- **`--no-upload` Flag**: Run the tool to generate the final audio file without uploading to S3. Perfect for testing configurations or local-only workflows.
- **Smart Config File Discovery**: The tool now searches for `config.cfg` in multiple standard locations (`./cfg/config.cfg`, `./config.cfg`, `./appu/config.cfg`), so you can run it from different directories.
- **macOS File Filtering**: Added `.gitignore` entries for macOS system files (`.DS_Store`, `.Spotlight-V100`, `._*`, etc.) to keep the repository clean.

## 🔧 Troubleshooting

### ❌ Config file not found
Ensure `config.cfg` exists in one of these locations:
- `./cfg/config.cfg` (from project root)
- `./config.cfg` (from project root)
- `./appu/config.cfg` (from project root)

Run with `-debug` flag to see which paths are being checked.

### ❌ S3 Upload Fails
- ✓ Verify AWS credentials are properly configured
- ✓ Check that `podcast_bucket` is not empty
- ✓ Ensure the S3 bucket exists and your credentials have write permissions
- ✓ Use `--no-upload` to skip upload and focus on audio processing

## 🛠️ Development

### ✅ Running Tests

```bash
cd appu
python -m pytest tests/
```

### 📦 Project Structure

```
appu/
├── appu.py              # Main entry point
├── audio.py             # Audio processing functions
├── cli.py               # CLI parsing and config loading
├── publish.py           # S3 upload functionality
├── config.cfg           # Example configuration
├── requirements.txt     # Python dependencies
└── tests/               # Unit tests
```

## 📄 License

See LICENSE.md in the project root.
