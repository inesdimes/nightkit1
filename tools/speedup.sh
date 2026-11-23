#!/bin/sh
# Format 3.0 item 5: speed the FINISHED mux up 1.2x. usage: tools/speedup.sh in_1x.mp4 out.mp4
ffmpeg -nostdin -v error -y -i "$1" -filter_complex "[0:v]setpts=PTS/1.2,fps=24[v];[0:a]atempo=1.2,acompressor=threshold=0.2:ratio=3:attack=5:release=80,loudnorm=I=-14:TP=-2.0[a]" -map "[v]" -map "[a]" -c:v libx264 -crf 17 -preset medium -pix_fmt yuv420p -c:a aac -b:a 192k -ar 48000 -movflags +faststart "$2"
