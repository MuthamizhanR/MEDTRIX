import os
import re

# --- CONFIGURATION ---
# This is the file providing the design (The one you renamed)
TEMPLATE_FILE = "template.html"
# This is the file that will be generated
OUTPUT_FILE = "index.html"
# ---------------------

def update_hub():
    print("--- MEDTRIX HUB UPDATER ---")

    # 1. Check if template exists
    if not os.path.exists(TEMPLATE_FILE):
        print(f"ERROR: Could not find '{TEMPLATE_FILE}'.")
        print("Please rename your design file to 'template.html' and try again.")
        return

    # 2. Scan for all Quiz HTML files
    files = [f for f in os.listdir('.') if f.endswith('.html')]
    quiz_files = []
    
    print("Scanning folder...")
    for f in files:
        # Exclude system files so they don't link to themselves
        if f in [TEMPLATE_FILE, OUTPUT_FILE, "old_index.html"]:
            continue
        quiz_files.append(f)
    
    quiz_files.sort()
    print(f"Found {len(quiz_files)} quiz files.")

    # 3. Generate the HTML Links for the hidden section
    # Your JavaScript reads these links to build the cards
    links_html = ""
    for filename in quiz_files:
        # Create a readable name (remove .html, replace underscores with spaces)
        display_name = filename.replace(".html", "").replace("_", " ").title()
        links_html += f'    <a href="{filename}">{display_name}</a>\n'

    # 4. Read the Template
    with open(TEMPLATE_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    # 5. SMART INJECT: Find the <div id="source-links"> and replace its content
    # This regex finds the div and replaces everything inside it safely
    pattern = r'(<div id="source-links">)([\s\S]*?)(</div>)'
    
    # Check if the marker exists in the template
    if "<div id=\"source-links\">" not in content:
        print("ERROR: Could not find <div id='source-links'> in your template.")
        print("Make sure your template.html has the hidden links section.")
        return

    # Perform the replacement
    new_content = re.sub(pattern, f'\\1\n{links_html}\\3', content)

    # 6. Save the new index.html
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print("------------------------------------------------")
    print(f"SUCCESS! Generated {OUTPUT_FILE} based on {TEMPLATE_FILE}.")
    print(f"It now contains links to {len(quiz_files)} quizzes.")
    print("You can now open index.html to see your site.")

if __name__ == "__main__":
    update_hub()