#!/bin/sh
# Format 3.0 x1.2 speed-up from the RAW parts: video without audio (out/<prefix>_video.mp4) + the script's unmastered mix (out/<audio>.wav).
# Use it instead of speedup.sh when the film starts on a loud hit: render_parts' loudnorm clips the first milliseconds.
# The audio is padded 0.5 s before loudnorm so the normaliser and the (4x oversampled) limiter are settled, then trimmed back.
# usage: tools/speedup_raw.sh out/bhb_video.mp4 out/boss_health_bar.wav out.mp4 <final seconds>
ffmpeg -nostdin -v error -y -i "$1" -i "$2" -filter_complex "[0:v]setpts=PTS/1.2,fps=24[v];[1:a]atempo=1.2,adelay=500:all=1,acompressor=threshold=0.2:ratio=3:attack=5:release=80,loudnorm=I=-13:TP=-2.0,aresample=192000,alimiter=limit=0.79:attack=1:release=60:level=false,aresample=48000,atrim=start=0.5:duration=$4,asetpts=PTS-STARTPTS[a]" -map "[v]" -map "[a]" -t "$4" -c:v libx264 -crf 17 -preset medium -pix_fmt yuv420p -c:a aac -b:a 192k -ar 48000 -movflags +faststart "$3"
