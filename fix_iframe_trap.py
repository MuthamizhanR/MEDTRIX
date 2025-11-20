import os
import re

# --- CONFIGURATION ---
TARGET_LINK = "qbanks.html"

# The NEW button with target="_top" (The "Break Out" command)
NEW_BUTTON_CODE = f"""
<a id="medtrix-nav-btn" href="{TARGET_LINK}" target="_top" style="
    position: fixed; 
    top: 15px; 
    left: 15px; 
    z-index: 99999; 
    background: #0056b3; 
    color: white; 
    padding: 10px 15px; 
    border-radius: 25px; 
    text-decoration: none; 
    font-family: sans-serif; 
    font-weight: bold; 
    box-shadow: 0 4px 6px rgba(0,0,0,0.2);
    border: 2px solid white;
    transition: transform 0.2s;
    cursor: pointer;
">
    &larr; Library
</a>
"""

def escape_iframe():
    print("--- FIXING IFRAME TRAP ---")
    
    files = [f for f in os.listdir('.') if f.endswith('.html')]
    # Skip main system files
    skip_files = ["index.html", "qbanks.html", "resources.html", "viewer.html"]
    
    count = 0
    
    for filename in files:
        if filename in skip_files:
            continue
            
        try:
            with open(filename, "r", encoding="utf-8") as f:
                content = f.read()
            
            # 1. REMOVE OLD BUTTON (Regex handles slight variations)
            # This looks for any link with id="medtrix-nav-btn" and deletes it
            clean_content = re.sub(r'<a id="medtrix-nav-btn".*?</a>', '', content, flags=re.DOTALL)
            
            # 2. Also remove the comment tag if it was separate
            clean_content = clean_content.replace("", "")
            
            # 3. INJECT NEW BUTTON (With target="_top")
            if "<body>" in clean_content:
                # Add new button right after body tag
                final_content = clean_content.replace("<body>", "<body>\n" + NEW_BUTTON_CODE)
                
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(final_content)
                    
                print(f"✅ Upgraded: {filename}")
                count += 1
                
        except Exception as e:
            print(f"❌ Error in {filename}: {e}")

    print("-" * 30)
    print(f"🎉 Success! Updated {count} quizzes to break out of iframes.")

if __name__ == "__main__":
    escape_iframe()