#!/usr/bin/env python3
import os
import re
import sys
import subprocess

# Configuration
IMAGE_DIR = 'files/images'
HTML_FILE = 'photo.html'

def update_html_and_push():
    # 1. Capture the custom description from command-line arguments
    custom_desc = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else None

    # 2. Get all images in the directory
    try:
        files = os.listdir(IMAGE_DIR)
    except FileNotFoundError:
        print(f"Error: Directory '{IMAGE_DIR}' not found.")
        return

    images = [f for f in files if f.lower().endswith(('.jpeg', '.jpg', '.png', '.webp'))]
    if not images:
        print(f"No images found in {IMAGE_DIR}.")
        return

    # Sort by the time the file was added (oldest at the top, newest at the END)
    images.sort(key=lambda x: os.path.getctime(os.path.join(IMAGE_DIR, x)))
    newest_image = images[-1] # The newest file is now the last item in the list

    # 3. Read the existing index.html to preserve old descriptions
    try:
        with open(HTML_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: File '{HTML_FILE}' not found.")
        return

    # Extract existing descriptions using regex to prevent overwriting past data
    existing_descriptions = {}
    matches = re.findall(r'<img src="[^"]*/([^"]+)" alt="([^"]*)"', content)
    for filename, alt_text in matches:
        existing_descriptions[filename] = alt_text

    # 4. Generate the new HTML block
    gallery_html = '<main class="gallery">\n'
    for img in images:
        # Determine the description for this specific image
        if img == newest_image and custom_desc:
            desc = custom_desc
        elif img in existing_descriptions:
            desc = existing_descriptions[img] # Reuse old description
        else:
            # Fallback: clean up the filename if no description exists
            desc = os.path.splitext(img)[0].replace('-', ' ').replace('_', ' ').title()
        
        gallery_html += f'        <div class="gallery-item">\n'
        gallery_html += f'            <img src="{IMAGE_DIR}/{img}" alt="{desc}" title="{desc}">\n'
        gallery_html += f'        </div>\n'
    gallery_html += '    </main>'

    # 5. Replace the existing <main> block
    new_content = re.sub(
        r'<main class="gallery">.*?</main>', 
        gallery_html, 
        content, 
        flags=re.DOTALL
    )

    # 6. Write the updated content
    with open(HTML_FILE, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("HTML updated successfully.")

    # 7. Execute Git commands
    try:
        print("Staging changes...")
        subprocess.run(['git', 'add', '.'], check=True)
        
        status = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True)
        if not status.stdout.strip():
            print("No changes to commit. Everything is up to date.")
            return

        print("Committing changes...")
        commit_msg = f"Add new photo: {custom_desc}" if custom_desc else "Auto-update gallery images"
        subprocess.run(['git', 'commit', '-m', commit_msg], check=True)
        
        print("Pushing to GitHub...")
        subprocess.run(['git', 'push'], check=True)
        print("Success! Live website updating.")
        
    except subprocess.CalledProcessError as e:
        print(f"An error occurred during git operations: {e}")

if __name__ == '__main__':
    update_html_and_push()
