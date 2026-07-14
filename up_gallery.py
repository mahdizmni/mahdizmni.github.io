#!/usr/bin/env python3
import os
import re
import sys
import subprocess
try:
    from PIL import Image
except ImportError:
    print("Error: The 'Pillow' library is required to create thumbnails.")
    print("Please install it by running: pip install Pillow")
    sys.exit(1)

# Configuration
IMAGE_DIR = 'files/images'
THUMB_DIR = 'files/thumbnails'
HTML_FILE = 'photos.html'
MAX_THUMB_SIZE = (800, 800) # Maximum width/height for thumbnails

def create_thumbnail(img_name):
    """Generates an optimized thumbnail if one doesn't already exist."""
    if not os.path.exists(THUMB_DIR):
        os.makedirs(THUMB_DIR)

    orig_path = os.path.join(IMAGE_DIR, img_name)
    thumb_path = os.path.join(THUMB_DIR, img_name)
    
    if not os.path.exists(thumb_path):
        print(f"Generating optimized thumbnail for {img_name}...")
        try:
            with Image.open(orig_path) as img:
                # Convert to RGB to prevent errors with certain image profiles
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
                # thumbnail() preserves aspect ratio and only shrinks images larger than max size
                img.thumbnail(MAX_THUMB_SIZE)
                img.save(thumb_path, format="JPEG", quality=85)
        except Exception as e:
            print(f"Error processing {img_name}: {e}")

def update_html_and_push():
    custom_desc = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else None

    try:
        files = os.listdir(IMAGE_DIR)
    except FileNotFoundError:
        print(f"Error: Directory '{IMAGE_DIR}' not found. Create it first.")
        return

    images = [f for f in files if f.lower().endswith(('.jpeg', '.jpg', '.png', '.webp'))]
    if not images:
        print(f"No images found in {IMAGE_DIR}.")
        return

    # Sort oldest to newest (newest at the end)
    images.sort(key=lambda x: os.path.getctime(os.path.join(IMAGE_DIR, x)))
    newest_image = images[-1]

    try:
        with open(HTML_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: File '{HTML_FILE}' not found.")
        return

    # Extract existing descriptions using a more flexible regex
    existing_descriptions = {}
    matches = re.findall(r'<img src="[^"]*/([^"]+)"[^>]*alt="([^"]*)"', content)
    for filename, alt_text in matches:
        existing_descriptions[filename] = alt_text

    # Generate thumbnails and build the new HTML block
    gallery_html = '<main class="gallery">\n'
    for img in images:
        create_thumbnail(img)

        if img == newest_image and custom_desc:
            desc = custom_desc
        elif img in existing_descriptions:
            desc = existing_descriptions[img]
        else:
            desc = os.path.splitext(img)[0].replace('-', ' ').replace('_', ' ').title()
        
        gallery_html += f'        <div class="gallery-item">\n'
        # Display the thumbnail, but store the original image path in data-fullres
        gallery_html += f'            <img src="{THUMB_DIR}/{img}" data-fullres="{IMAGE_DIR}/{img}" alt="{desc}" title="{desc}" onclick="openLightbox(this)">\n'
        gallery_html += f'        </div>\n'
    gallery_html += '    </main>'

    new_content = re.sub(
        r'<main class="gallery">.*?</main>', 
        gallery_html, 
        content, 
        flags=re.DOTALL
    )

    with open(HTML_FILE, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("HTML updated successfully.")

    try:
        print("Staging changes...")
        subprocess.run(['git', 'add', '.'], check=True)
        
        status = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True)
        if not status.stdout.strip():
            print("No changes to commit. Everything is up to date.")
            return

        print("Committing changes...")
        commit_msg = f"Add new photo: {custom_desc}" if custom_desc else "Auto-update gallery images and thumbnails"
        subprocess.run(['git', 'commit', '-m', commit_msg], check=True)
        
        print("Pushing to GitHub...")
        subprocess.run(['git', 'push'], check=True)
        print("Success! Live website updating.")
        
    except subprocess.CalledProcessError as e:
        print(f"An error occurred during git operations: {e}")

if __name__ == '__main__':
    update_html_and_push()
