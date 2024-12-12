#!/bin/bash

for file in *.mp4; do
  [ -e "$file" ] || continue
  base_name=$(basename "$file" .mp4)
  compressed_file="${base_name}_compressed.mp4"
  ffmpeg -i "$file" -vcodec libx264 -crf 28 -preset slower "$compressed_file"
  gif_file="${base_name}.gif"
  ffmpeg -i "$compressed_file" -vf "fps=15,scale=iw:-1:flags=lanczos" -c:v gif "$gif_file"
  optimized_gif="${base_name}_optimized.gif"
  gifsicle --optimize=3 --colors 256 "$gif_file" > "$optimized_gif"
  final_gif="${base_name}.gif"
  mv "$optimized_gif" "$final_gif"
  rm "$compressed_file"
  rm "$gif_file"
done
