import re

TARGET_FILE = "resources.html"

def clean_page():
    print("--- REMOVING REDUNDANT BUTTON ---")
    
    try:
        with open(TARGET_FILE, "r", encoding="utf-8") as f:
            content = f.read()

        # Regex to find the "View My Progress" button block
        # It looks for the specific inline style and text
        pattern = r'<div style="text-align: center; margin-bottom: 20px;">\s*<button onclick="openStats\(\)".*?View My Progress\s*</button>\s*</div>'
        
        # Remove it
        if re.search(pattern, content, re.DOTALL):
            new_content = re.sub(pattern, "", content, flags=re.DOTALL)
            
            with open(TARGET_FILE, "w", encoding="utf-8") as f:
                f.write(new_content)
            print("✅ Removed 'View My Progress' button from resources page.")
        else:
            print("⚠️ Button not found (Maybe already removed).")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    clean_page()