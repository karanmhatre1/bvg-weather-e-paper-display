# epd_image.py

import numpy as np
import cv2
import re

def image_to_bin(in_path, out_path, width, height, invert=False):
    img = cv2.imread(in_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise RuntimeError(f"Could not read image: {in_path}")

    img = cv2.resize(img, (width, height), interpolation=cv2.INTER_AREA)
    _, bw = cv2.threshold(img, 128, 255, cv2.THRESH_BINARY)

    if invert:
        bw = 255 - bw

    buf = np.full((height * width // 8,), 0xFF, dtype=np.uint8)

    for y in range(height):
        for x in range(width):
            pixel = bw[y, x]  # 0 or 255
            if pixel == 0:    # black pixel
                index = (x // 8) + y * (width // 8)
                bit = 0x80 >> (x % 8)
                buf[index] &= (~bit & 0xFF)

    buf.tofile(out_path)

REPLACEMENTS = [
    (r'\bHauptbahnhof\b', 'Hbf'),
    (r'\bBahnhof\b', 'Bhf'),
    (r'\bStraße\b', 'Str.'),
    (r'\bStrasse\b', 'Str.'),
    (r'\bStr\.\b', 'Str.'),      # normalise different Str. variants
    (r'\bPlatz\b', 'Pl.'),
]

def shorten_stop_name(name: str, max_len: int = 12) -> str:
    s = name

    # 1) Remove trailing city in brackets, e.g. " (Berlin)"
    s = re.sub(r'\s*\([^)]*\)\s*$', '', s)

    # 2) Remove leading "S ", "U ", or "S+U "
    s = re.sub(r'^(S\+U|S|U)\s+', '', s)

    # 3) Apply word-level replacements
    for pattern, repl in REPLACEMENTS:
        s = re.sub(pattern, repl, s)

    # 4) Normalise whitespace
    s = re.sub(r'\s+', ' ', s).strip()

    # 5) Truncate smart-ish to max_len
    if len(s) > max_len:
        cut = s[:max_len]
        # try to cut on last space, but only if it's not too early
        last_space = cut.rfind(' ')
        if last_space >= max_len // 2:
            cut = cut[:last_space]
        s = cut.rstrip()

    return s	