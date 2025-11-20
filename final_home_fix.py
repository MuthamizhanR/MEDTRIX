import re

TARGET_FILE = "index.html"

# The New Button we want
REVISION_BUTTON = """
        <a href="revision.html" class="menu-card">
            <div class="icon">🧠</div>
            <div class="card-title">Active Recall</div>
            <p class="card-desc">Spaced repetition flashcards from your missed questions.</p>
        </a>
"""

def fix_home():
    print("--- FINAL HOME PAGE FIX ---")
    
    with open(TARGET_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. REMOVE OLD MOCK TEST CARD (Matches various forms)
    # We look for any card linking to mocks.html OR qbanks.html that has a clock icon
    mock_pattern = r'<a href="(mocks\.html|qbanks\.html)" class="menu-card">.*?<div class="icon">⏱️</div>.*?</a>'
    
    if re.search(mock_pattern, content, re.DOTALL):
        # Replace the Mock Card with the Revision Card
        new_content = re.sub(mock_pattern, REVISION_BUTTON.strip(), content, flags=re.DOTALL)
        print("✅ Swapped Mock Test button for Active Recall.")
    else:
        print("⚠️ Mock Test button not found. Checking if Revision button already exists...")
        if "Active Recall" in content:
            print("ℹ️ Active Recall button is already present.")
            new_content = content
        else:
            # If neither exists, we might need to append it manually or check the file structure
            print("❌ Could not find insertion point. Please check index.html manually.")
            new_content = content

    # 2. ENSURE ANALYTICS LINK IS CORRECT
    # Just to be safe, force the analytics link
    if 'href="resources.html" class="menu-card"' in new_content:
         new_content = new_content.replace('href="resources.html" class="menu-card"', 'href="analytics.html" class="menu-card"')
         print("✅ Verified Analytics Link.")

    with open(TARGET_FILE, "w", encoding="utf-8") as f:
        f.write(new_content)

if __name__ == "__main__":
    fix_home()