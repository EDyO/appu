import re
import sys
from audio import load_mp3 , load_mp4
from cli import parse_config
import subprocess

cfg = parse_config()

if len(sys.argv) < 2:
    print("Usage: youappu.py <audio_podcast_file>")
    sys.exit(1)

audio_podcast_file = sys.argv[1]

print("Transforming audio podcast into video")

video = load_mp3(audio_podcast_file)

video.export(
    cfg['tmp_file'],
    format="mp4",
    parameters=["-loop", "1" , 
        "-i", cfg['cover_file'], 
        "-c:v", "libx264", 
        "-vf", "pad=ceil(iw/2)*2:ceil(ih/2)*2",         
        # "-filter_complex", "[0:a]showwaves=colors=0xff1646@0.3:scale=sqrt:mode=cline,format=yuva420p[v];[v]scale=1280:400[bg];[v][bg]overlay=(W-w)/2:H-h[outv]",
        #"-map", "[outv]",       
        "-shortest"
    ]
)

print("Inserting audio waves into video")


command="ffmpeg -i " + cfg['tmp_file'] +\
    " -filter_complex \"[0:a]showwaves=colors=0xff1646@0.3" + \
    ":scale=sqrt:mode=cline,format=yuva420p[v];" +\
    "[v]scale=1280:400[bg];"+\
    "[v][bg]overlay=(W-w)/2:H-h[outv]\"" +\
    " -map \"[outv]\" -map 0:a -c:v libx264 -c:a copy "+ \
    cfg['final_file']

print (f"Command: {command}")


def execute_command(command):
    try:
        resultado = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"Salida: {resultado.stdout.decode('utf-8')}")
        print(f"Errores: {resultado.stderr.decode('utf-8')}")
    except subprocess.CalledProcessError as e:
        print(f"Error al ejecutar el command: {e}")

execute_command(command)
