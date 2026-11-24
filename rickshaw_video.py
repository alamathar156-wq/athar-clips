#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Athar Clips - "Rickshaw Wala" Episode 1
30 second vertical stickman short  (1080x1920, 30 fps, 5 scenes x 6 sec)

Needs : Python 3.9+, Pillow (with libraqm, for Urdu letter joining), ffmpeg
Font  : Noto Naskh Arabic Bold (free, Google Fonts). Put NotoNaskhArabic-Bold.ttf
        next to this file, or set  URDU_FONT=/path/to/font.ttf
Run   : python rickshaw_video.py             -> rickshaw_ep1.mp4
        python rickshaw_video.py --preview   -> preview.png  (6 test frames)
"""
import functools
import math
import os
import shutil
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor

from PIL import Image, ImageDraw, ImageFont

# ----------------------------------------------------------------- settings
W, H, FPS = 1080, 1920, 30
SCENE_SEC = 6
NF = SCENE_SEC * FPS          # frames per scene
ANIM_TOP, AH = 150, 1150      # animation area on screen
G = 930                       # ground line (inside animation area)
SS = 2                        # supersampling for smooth lines
HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.environ.get("OUT_DIR", HERE)

WHITE = (255, 255, 255)
BLACK = (20, 20, 20)
GREY = (205, 205, 205)
GREEN = (36, 150, 88)
YELLOW = (255, 200, 40)
RED = (222, 52, 52)
BLUE = (70, 140, 230)
MONEY = (130, 200, 140)
CREAM = (255, 243, 205)


def find_font(cands):
    for c in cands:
        if c and os.path.exists(c):
            return c
    return None


FONT = find_font([
    os.environ.get("URDU_FONT"),
    os.path.join(HERE, "NotoNaskhArabic-Bold.ttf"),
    "/usr/share/fonts/truetype/noto/NotoNaskhArabic-Bold.ttf",
    "/usr/share/fonts/truetype/freefont/FreeSerifBold.ttf",
])
LATIN = find_font([
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "C:/Windows/Fonts/arialbd.ttf",
    "/Library/Fonts/Arial Bold.ttf",
    FONT,
])
if not FONT:
    sys.exit("Urdu font nahi mila - NotoNaskhArabic-Bold.ttf yahan rakh dein.")


@functools.lru_cache(None)
def font(path, size):
    return ImageFont.truetype(path, int(size), layout_engine=ImageFont.Layout.RAQM)


# ------------------------------------------------------------------ helpers
def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def prog(t, t0, t1):
    return clamp((t - t0) / (t1 - t0))


def eo(x):
    return 1 - (1 - x) ** 3


def eio(x):
    return 3 * x * x - 2 * x ** 3


def lerp(a, b, k):
    return a + (b - a) * k


class Pen:
    """Small drawing helper: all coordinates are in 1080-wide animation space."""

    def __init__(self, img):
        self.d = ImageDraw.Draw(img)

    def line(self, pts, w=10, c=BLACK):
        p = [(x * SS, y * SS) for x, y in pts]
        self.d.line(p, fill=c, width=max(1, int(w * SS)), joint="curve")
        r = w * SS / 2
        for x, y in (p[0], p[-1]):
            self.d.ellipse((x - r, y - r, x + r, y + r), fill=c)
