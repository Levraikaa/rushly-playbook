#!/bin/zsh
# Télécharge une ou plusieurs vidéos dans un dossier neuf et les transcrit. Usage : recuperer.sh <dossier> <url>...
R="${0:A:h}"; D="$1"; shift; mkdir -p "$D"; cd "$D" || exit 1
for u in "$@"; do
  for try in 1 2 3 4 5; do
    o=$("$R/venv/bin/yt-dlp" --no-warnings --no-playlist -f "b[vcodec^=h264]/b" -o "%(id)s.%(ext)s" --print after_move:"%(id)s|%(uploader)s|%(like_count)s|%(comment_count)s|%(duration)s|%(description).220s" "$u" 2>&1 | grep -v Deprecated | tail -1 | cut -c1-340)
    case "$o" in ERROR*) sleep 4;; *) echo "$o"; break;; esac
  done
done
"$R/venv/bin/python" -I "$R/veille.py" "$D"/*.mp4 2>&1 | grep -v "Warning\|warn"
