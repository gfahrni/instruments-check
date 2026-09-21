#!/usr/bin/env python3
"""Telecharge les images des cartes de cartes.json dans cartes/ (offline, GitHub Pages).

Usage: python3 telecharger-cartes.py
Relit cartes.json (genere depuis cartes-collections.md), telecharge chaque image
laststicker.com manquante, en parallele. Ne retelecharge pas les fichiers deja presents.
"""
import json
import os
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
JSON = os.path.join(HERE, "cartes.json")
BASE = "https://www.laststicker.com/i/cards/"
COLL = {"mario": "7386", "disney": "1481"}


def url_for(img):
    # img = "cartes/mario/le5.jpg" -> https://.../7386/le5.jpg
    parts = img.split("/")
    return BASE + COLL[parts[1]] + "/" + parts[2]


def fetch(img):
    dest = os.path.join(HERE, img)
    if os.path.exists(dest) and os.path.getsize(dest) > 0:
        return img, True
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    u = url_for(img)
    for attempt in range(4):
        try:
            req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"})
            data = urllib.request.urlopen(req, timeout=30).read()
            if not data.startswith(b"\xff\xd8"):
                raise ValueError("pas un jpeg")
            with open(dest, "wb") as f:
                f.write(data)
            return img, True
        except Exception as e:
            if attempt == 3:
                print("!!", img, e, flush=True)
                return img, False
    return img, False


def main():
    data = json.load(open(JSON, encoding="utf-8"))
    imgs = []
    seen = set()
    for kid in data.values():
        for c in kid["cartes"]:
            if c["img"] not in seen:
                seen.add(c["img"])
                imgs.append(c["img"])
    print("images a telecharger:", len(imgs), flush=True)
    ok = 0
    with ThreadPoolExecutor(max_workers=12) as ex:
        for img, good in ex.map(fetch, imgs):
            ok += 1 if good else 0
    print("OK:", ok, "/", len(imgs), flush=True)
    return 0 if ok == len(imgs) else 1


if __name__ == "__main__":
    sys.exit(main())
