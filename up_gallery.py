#!/usr/bin/env python3
import os
import re
import subprocess

# Configuration
IMAGE_DIR = 'files/images'
HTML_FILE = 'photo.html'

def update_html_and_push():
    # 1. Get all images in the directory
    try:
        files = os.listdir(IMAGE_DIR)
    except FileNotFoundError:
        print(f"Error: Directory '{IMAGE_DIR}' not found.")
        return

    images = [f for f in files if f.lower().endswith(('.jpeg', '.jpg', '.png', '.webp'))]
    images.sort() # Sorts alphabetically

    if not images:
        print(f"No images found in {IMAGE_DIR}.")
        return

    # 2. Generate the new HTML block
    gallery_html = '<main class="gallery">\n'
    for img in images:
        # Create a readable title from the filename (e.g., "dark_sky.jpeg" -> "Dark Sky")
        clean_title = os.path.splitext(img)[0].replace('-', ' ').replace('_', ' ').title()
        
        gallery_html += f'        <div class="gallery-item">\n'
        gallery_html += f'            <img src="{IMAGE_DIR}/{img}" alt="{clean_title}" title="{clean_title}">\n'
        gallery_html += f'        </div>\n'
    gallery_html += '    </main>'

    # 3. Read the existing index.html
    try:
        with open(HTML_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: File '{HTML_FILE}' not found.")
        return

    # 4. Replace the existing <main> block with the new one
    # This regex looks for the <main class="gallery"> tag and everything inside it
    new_content = re.sub(
        r'<main class="gallery">.*?</main>', 
        gallery_html, 
        content, 
        flags=re.DOTALL
    )

    # 5. Write the updated content back to index.html
    with open(HTML_FILE, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("HTML updated successfully with current images.")

    # 6. Execute Git commands
    try:
        print("Staging changes...")
        subprocess.run(['git', 'add', '.'], check=True)
        
        # Check if there are actually changes to commit
        status = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True)
        if not status.stdout.strip():
            print("No changes to commit. Everything is up to date.")
            return

        print("Committing changes...")
        subprocess.run(['git', 'commit', '-m', 'Auto-update gallery images'], check=True)
        
        print("Pushing to GitHub...")
        subprocess.run(['git', 'push'], check=True)
        print("Success! Live website updating.")
        
    except subprocess.CalledProcessError as e:
        print(f"An error occurred during git operations: {e}")

if __name__ == '__main__':
    update_html_and_push()
