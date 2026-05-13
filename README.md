# Catering Slideshow — GitHub Pages Setup

## Folder structure
```
slideshow/
├── index.html               ← the slideshow (don't touch)
├── generate_images_json.py  ← run this when you add/remove photos
└── photos/
    ├── images.json          ← auto-generated list of photos
    ├── photo01.jpg
    ├── photo02.jpg
    └── ...
```

---

## First time setup

### Step 1 — Create a GitHub account
Go to https://github.com and sign up (free).

### Step 2 — Create a new repository
1. Click the **+** icon (top right) → **New repository**
2. Name it: `slideshow` (or anything you like)
3. Set it to **Public**
4. Click **Create repository**

### Step 3 — Upload your files
1. Click **"uploading an existing file"** link on the repo page
2. Drag and drop these items:
   - `index.html`
   - The entire `photos/` folder with all your images and `images.json`
3. Scroll down, click **Commit changes**

### Step 4 — Enable GitHub Pages
1. Go to your repo → **Settings** tab
2. Click **Pages** in the left sidebar
3. Under "Branch" select **main** → click **Save**
4. Wait 1–2 minutes

### Step 5 — Get your URL
Your slideshow is now live at:
```
https://YOUR-USERNAME.github.io/slideshow/
```
Open this URL in your Philips TV browser — done!

---

## Adding or changing photos

1. Add/remove photos from the `photos/` folder on your computer
2. Run `generate_images_json.py` (double-click or run with Python):
   ```
   python generate_images_json.py
   ```
   This updates `photos/images.json` automatically.
3. Go to your GitHub repo → `photos/` folder
4. Click **Add file → Upload files**
5. Upload the new photos + the updated `images.json`
6. Click **Commit changes**
7. Wait 1 minute — your TV URL updates automatically!

---

## Updating the TV
Just refresh the browser on the TV — it always loads the latest photos from GitHub.
