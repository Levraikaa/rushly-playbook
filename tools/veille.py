"""Pour la Veille : transcrit une vidéo et en tire une petite image.

Usage : veille.py <video.mp4>... (écrit <video>.json à côté de chaque vidéo)
"""
import base64
import io
import json
import sys

import av
from faster_whisper import WhisperModel
from PIL import Image

model = WhisperModel("small", device="cpu", compute_type="int8")

for path in sys.argv[1:]:
    if path.rsplit("/", 1)[-1] and __import__("os").path.getsize(path) < 1000:
        print("Fichier invalide, lien à recopier :", path)
        continue
    with av.open(path) as box:
        stream = box.streams.video[0]
        box.seek(int(1.0 / stream.time_base), stream=stream)
        frame = next(box.decode(stream))
        img = frame.to_image()
    img.thumbnail((240, 427))
    buf = io.BytesIO()
    img.save(buf, "JPEG", quality=70)
    thumb = "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()

    segments, info = model.transcribe(path, vad_filter=True)
    texte = " ".join(s.text.strip() for s in segments)
    out = path.rsplit(".", 1)[0] + ".json"
    with open(out, "w") as f:
        json.dump({"thumb": thumb, "transcription": texte}, f, ensure_ascii=False)
    print(path.rsplit("/", 1)[-1], info.language, round(info.language_probability, 2), len(buf.getvalue()), "o")
    print(texte)
