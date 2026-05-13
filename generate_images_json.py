# Scans the photos/ directory for image files and writes their filenames to photos/images.json.
import os, json

photos_dir = os.path.join(os.path.dirname(__file__), "photos")
exts = {".jpg", ".jpeg", ".png", ".webp"}

files = sorted([
    f for f in os.listdir(photos_dir)
    if os.path.splitext(f)[1].lower() in exts
])

out = os.path.join(photos_dir, "images.json")
with open(out, "w") as f:
    json.dump(files, f, indent=2)

print(f"Generated images.json with {len(files)} photos:")
for name in files:
    print(f"  {name}")
