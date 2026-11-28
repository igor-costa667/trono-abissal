#!/bin/bash
# Acabamento HyperFrames (Igor, 28/11/2026): cartão animado "Seguir @tronoabissal"
# nos últimos 4,5 s do episódio (em cima do cartão A ou B).
# Uso: bash serie/hyperframes_final.sh saida_vertical.mp4 saida_hf.mp4
# Sai com erro se algo falhar: aí a rotina publica o saida_vertical.mp4 como sempre.
set -euo pipefail
ENT=$(realpath "$1"); SAI=$(realpath -m "$2")
SERIE=$(cd "$(dirname "$0")" && pwd)
W=/home/claude/hf_trono; rm -rf "$W"; mkdir -p "$W"; cp -r "$SERIE/hyperframes/." "$W/"
cd "$W"
timeout 300 npm i --silent --no-audit --no-fund >/dev/null 2>&1
DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$ENT")
CAUDA=6.5
T=$(python3 -c "print(round($DUR-$CAUDA,3))")
ffmpeg -loglevel error -y -i "$ENT" -t "$T" -c:v libx264 -preset veryfast -crf 16 -c:a aac -b:a 192k cabeca.mp4
ffmpeg -loglevel error -y -ss "$T" -i "$ENT" -c:v libx264 -preset veryfast -crf 16 -c:a aac -b:a 192k trecho.mp4
TD=$(ffprobe -v error -show_entries format=duration -of csv=p=0 trecho.mp4)
INI=$(python3 -c "print(round(max(0,$TD-4.5),3))")
sed -i "s/__DUR__/$TD/; s/__INI__/$INI/" index.html
HYPERFRAMES_SKIP_SKILLS=1 timeout 600 npx hyperframes render -o cauda.mp4 >render.log 2>&1 || { tail -20 render.log; exit 1; }
ffmpeg -loglevel error -y -i cabeca.mp4 -i cauda.mp4 -filter_complex "[0:v]fps=30,scale=1080:1920,setsar=1[v0];[1:v]fps=30,scale=1080:1920,setsar=1[v1];[0:a]aresample=44100,aformat=channel_layouts=stereo[a0];[1:a]aresample=44100,aformat=channel_layouts=stereo[a1];[v0][a0][v1][a1]concat=n=2:v=1:a=1[v][a]" -map "[v]" -map "[a]" -c:v libx264 -preset veryfast -crf 16 -c:a aac -b:a 192k "$SAI"
NOVA=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$SAI")
python3 -c "import sys; sys.exit(0 if abs($NOVA-$DUR)<0.3 else 1)" || { echo "duração mudou ($DUR -> $NOVA)"; exit 1; }
echo "ok $SAI"
