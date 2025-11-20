import re
import os

TARGET_FILE = "index.html"

# The Perfect 4-Button Grid
NEW_MENU_HTML = """
    <div class="main-container">
        
        <!-- 1. Q-BANKS (Library) -->
        <a href="qbanks.html" class="menu-card">
            <div class="icon">🩺</div>
            <div class="card-title">Q-Bank Archive</div>
            <p class="card-desc">Access the full library of 170+ topic-wise question banks.</p>
        </a>

        <!-- 2. STUDY RESOURCES (Notes) -->
        <a href="resources.html" class="menu-card">
            <div class="icon">📚</div>
            <div class="card-title">Study Resources</div>
            <p class="card-desc">High-yield notes, PDFs, and quick revision charts.</p>
        </a>

        <!-- 3. ANALYTICS (Stats) -->
        <a href="analytics.html" class="menu-card">
            <div class="icon">📊</div>
            <div class="card-title">My Analytics</div>
            <p class="card-desc">Track your progress and completion stats.</p>
        </a>

        <!-- 4. ACTIVE RECALL (Flashcards) -->
        <a href="revision.html" class="menu-card">
            <div class="icon">🧠</div>
            <div class="card-title">Active Recall</div>
            <p class="card-desc">Spaced repetition flashcards from your missed questions.</p>
        </a>

    </div>
"""

def restore_menu():
    print("--- RESTORING MAIN MENU ---")
    
    if not os.path.exists(TARGET_FILE):
        print(f"❌ Error: {TARGET_FILE} not found.")
        return

    with open(TARGET_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    # Find the main container block and replace it entirely
    # Matches <div class="main-container"> ... </div>
    # We use DOTALL to match across newlines
    pattern = r'<div class="main-container">.*?</div>'
    
    # Safety check: Does the file have a main container?
    if '<div class="main-container">' in content:
        # Replace the old/broken grid with the new perfect grid
        # We use a non-greedy match (.*?) to find the closing div
        # NOTE: This simple regex assumes the main-container doesn't have nested divs that end with </div> immediately. 
        # Since our menu structure is simple, this usually works. 
        # A safer way is to replace the whole body content between header and footer if needed, 
        # but let's try the container replacement first.
        
        # Actually, a safer regex for nested content is hard. 
        # Let's just find the START of the container and the START of the footer, and replace everything in between.
        
        start_marker = '<div class="main-container">'
        end_marker = '<footer>'
        
        start_idx = content.find(start_marker)
        end_idx = content.find(end_marker)
        
        if start_idx != -1 and end_idx != -1:
            before = content[:start_idx]
            after = content[end_idx:]
            new_content = before + NEW_MENU_HTML + "\n\n    " + after
            
            with open(TARGET_FILE, "w", encoding="utf-8") as f:
                f.write(new_content)
            print("✅ Menu restored successfully with all 4 buttons.")
        else:
            print("❌ Could not find the menu container markers. Check file structure.")
    else:
        print("❌ 'main-container' div not found.")

if __name__ == "__main__":
    restore_menu()