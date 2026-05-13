#!/usr/bin/env python3
"""
Catering Slideshow MP4 Generator
Reads photos from /mnt/user-data/uploads/, generates a 1920x1080 MP4
with crossfade transitions and warm catering-style text overlays.
"""

import os
import sys
import subprocess
import glob
import shutil
import textwrap
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np

# ── CONFIG ──────────────────────────────────────────────────
OUTPUT_PATH   = "/mnt/user-data/outputs/catering-slideshow.mp4"
WORK_DIR      = "/home/claude/slideshow_frames"
W, H          = 1920, 1080
FPS           = 30
HOLD_SECS     = 5       # seconds each photo is fully visible
FADE_SECS     = 1.2     # crossfade duration in seconds
HOLD_FRAMES   = int(HOLD_SECS * FPS)
FADE_FRAMES   = int(FADE_SECS * FPS)

# Warm palette
BG_COLOR      = (26, 14, 8)
GOLDEN        = (212, 131, 42)
CREAM         = (253, 246, 236)
TAN           = (237, 217, 190)
OVERLAY_TOP   = (15, 7, 3, 0)      # transparent
OVERLAY_BOT   = (15, 7, 3, 237)    # ~93% opaque

# Captions — None = photo-only slide
CAPTIONS = [
    {"tag": "OUR SERVICES",  "title": "Crafted with Love",      "desc": "Every dish prepared fresh, with ingredients chosen for flavor and quality."},
    {"tag": "CATERING",      "title": "Events to Remember",     "desc": "From intimate gatherings to grand celebrations — we handle every detail."},
    None,
    {"tag": "MENU",          "title": "Flavors that Delight",   "desc": "A menu built around taste, tradition, and the joy of sharing a great meal."},
    {"tag": "PRESENTATION",  "title": "Beautiful Presentation", "desc": "We believe food should be as beautiful to look at as it is delicious to eat."},
    None,
    None,
]

# ── FIND PHOTOS ─────────────────────────────────────────────
UPLOAD_DIR = "/mnt/user-data/uploads"
exts = ["*.jpg", "*.jpeg", "*.png", "*.webp", "*.JPG", "*.JPEG", "*.PNG"]
photos = []
for ext in exts:
    photos.extend(glob.glob(os.path.join(UPLOAD_DIR, ext)))
photos = sorted(set(photos))

if not photos:
    print("ERROR: No photos found in", UPLOAD_DIR)
    print("Please upload your photos first.")
    sys.exit(1)

print(f"Found {len(photos)} photos: {[os.path.basename(p) for p in photos]}")

# ── FONT SETUP ───────────────────────────────────────────────
def find_font(size, bold=False):
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSerif.ttf",
    ]
    sans = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]
    search = candidates if not bold else candidates
    for path in (search + sans):
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except:
                continue
    return ImageFont.load_default()

font_tag   = find_font(22)
font_title = find_font(72, bold=True)
font_desc  = find_font(30)

# ── FRAME HELPERS ────────────────────────────────────────────
def photo_to_frame(path):
    """Load photo, fit to 1920x1080 with dark bg, no cropping."""
    img = Image.open(path).convert("RGB")
    img.thumbnail((W, H), Image.LANCZOS)
    frame = Image.new("RGB", (W, H), BG_COLOR)
    x = (W - img.width) // 2
    y = (H - img.height) // 2
    frame.paste(img, (x, y))
    return frame

def draw_gradient_overlay(frame):
    """Draw bottom-to-top dark gradient for text legibility."""
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    grad_height = int(H * 0.55)
    for i in range(grad_height):
        t = i / grad_height  # 0=bottom, 1=top
        alpha = int(OVERLAY_BOT[3] * (1 - t))
        y = H - 1 - i
        draw.line([(0, y), (W, y)], fill=(OVERLAY_BOT[0], OVERLAY_BOT[1], OVERLAY_BOT[2], alpha))
    frame_rgba = frame.convert("RGBA")
    frame_rgba = Image.alpha_composite(frame_rgba, overlay)
    return frame_rgba.convert("RGB")

def wrap_text(text, font, max_width):
    """Wrap text to fit within max_width pixels."""
    words = text.split()
    lines = []
    current = ""
    dummy = Image.new("RGB", (1, 1))
    d = ImageDraw.Draw(dummy)
    for word in words:
        test = (current + " " + word).strip()
        bbox = d.textbbox((0, 0), test, font=font)
        if bbox[2] - bbox[0] <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines

def draw_caption(frame, caption):
    """Draw tag, title, divider, description onto frame."""
    frame = draw_gradient_overlay(frame)
    draw = ImageDraw.Draw(frame)

    margin_left = 80
    margin_bottom = 80
    max_text_w = W // 2

    # Measure everything from bottom up
    desc_lines = wrap_text(caption["desc"], font_desc, max_text_w)
    desc_line_h = 44
    desc_h = len(desc_lines) * desc_line_h

    divider_h = 16
    title_bbox = draw.textbbox((0, 0), caption["title"], font=font_title)
    title_h = title_bbox[3] - title_bbox[1] + 8
    tag_bbox = draw.textbbox((0, 0), caption["tag"], font=font_tag)
    tag_h = tag_bbox[3] - tag_bbox[1] + 14

    total_h = tag_h + title_h + divider_h + desc_h
    y = H - margin_bottom - total_h

    # Tag
    draw.text((margin_left, y), caption["tag"], font=font_tag, fill=GOLDEN)
    y += tag_h

    # Title (with subtle shadow)
    draw.text((margin_left + 2, y + 2), caption["title"], font=font_title, fill=(0, 0, 0, 120))
    draw.text((margin_left, y), caption["title"], font=font_title, fill=CREAM)
    y += title_h

    # Divider
    draw.rectangle([(margin_left, y), (margin_left + 52, y + 2)], fill=GOLDEN)
    y += divider_h

    # Description
    for line in desc_lines:
        draw.text((margin_left, y), line, font=font_desc, fill=(*TAN, 230))
        y += desc_line_h

    return frame

def crossfade(frame_a, frame_b, t):
    """Blend two frames. t=0 → frame_a, t=1 → frame_b."""
    a = np.array(frame_a, dtype=np.float32)
    b = np.array(frame_b, dtype=np.float32)
    blended = (a * (1 - t) + b * t).astype(np.uint8)
    return Image.fromarray(blended)

# ── PREPARE WORK DIR ─────────────────────────────────────────
if os.path.exists(WORK_DIR):
    shutil.rmtree(WORK_DIR)
os.makedirs(WORK_DIR)

# ── BUILD FRAMES ─────────────────────────────────────────────
print("Rendering frames...")
frame_index = 0

def save_frame(img):
    global frame_index
    img.save(os.path.join(WORK_DIR, f"frame_{frame_index:06d}.jpg"), quality=92)
    frame_index += 1

rendered_slides = []
for i, photo_path in enumerate(photos):
    cap = CAPTIONS[i % len(CAPTIONS)]
    base = photo_to_frame(photo_path)
    if cap:
        slide = draw_caption(base, cap)
    else:
        slide = base
    rendered_slides.append(slide)
    print(f"  Rendered slide {i+1}/{len(photos)}: {os.path.basename(photo_path)}")

# Write frames: hold + crossfade between each slide
for i, slide in enumerate(rendered_slides):
    next_slide = rendered_slides[(i + 1) % len(rendered_slides)]

    # Hold frames
    for _ in range(HOLD_FRAMES):
        save_frame(slide)

    # Crossfade frames
    for f in range(FADE_FRAMES):
        t = f / FADE_FRAMES
        blended = crossfade(slide, next_slide, t)
        save_frame(blended)

total_frames = frame_index
duration_secs = total_frames / FPS
print(f"Total frames: {total_frames} ({duration_secs:.1f} seconds)")

# ── ENCODE MP4 ───────────────────────────────────────────────
print("Encoding MP4...")
cmd = [
    "ffmpeg", "-y",
    "-framerate", str(FPS),
    "-i", os.path.join(WORK_DIR, "frame_%06d.jpg"),
    "-c:v", "libx264",
    "-preset", "slow",
    "-crf", "18",           # high quality (lower = better, 18 is excellent)
    "-pix_fmt", "yuv420p",  # max TV compatibility
    "-movflags", "+faststart",
    OUTPUT_PATH
]
result = subprocess.run(cmd, capture_output=True, text=True)
if result.returncode != 0:
    print("FFmpeg error:", result.stderr[-500:])
    sys.exit(1)

size_mb = os.path.getsize(OUTPUT_PATH) / 1024 / 1024
print(f"Done! Saved to {OUTPUT_PATH} ({size_mb:.1f} MB)")

# Cleanup
shutil.rmtree(WORK_DIR)
print("Temporary frames cleaned up.")
