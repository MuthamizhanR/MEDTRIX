import os

# --- CONFIGURATION ---
TARGET_LINK = "qbanks.html"

# We compress the button code slightly to make it easier to inject cleanly
BUTTON_HTML = f"""
<a id="medtrix-nav-btn" href="{TARGET_LINK}" style="position:fixed;top:15px;left:15px;z-index:99999;background:#0056b3;color:white;padding:10px 15px;border-radius:25px;text-decoration:none;font-family:sans-serif;font-weight:bold;box-shadow:0 4px 6px rgba(0,0,0,0.2);border:2px solid white;transition:transform 0.2s;cursor:pointer;">&larr; Library</a>
"""

def fast_fix():
    print("--- FAST NAVIGATION FIX ---")
    
    files = [f for f in os.listdir('.') if f.endswith('.html')]
    skip_files = ["index.html", "qbanks.html", "resources.html", "viewer.html", "template.html"]
    
    count = 0
    skipped = 0
    
    for i, filename in enumerate(files):
        if filename in skip_files:
            continue
            
        try:
            with open(filename, "r", encoding="utf-8") as f:
                content = f.read()
            
            # CHECK 1: Is the button already there?
            if 'id="medtrix-nav-btn"' in content:
                # It exists. Let's not touch it to prevent hangs.
                print(f"[{i}] {filename}: ✅ Already has button")
                skipped += 1
                continue
            
            # CHECK 2: Find body tag
            if "<body>" in content:
                # Simple string replace - instant, no searching
                new_content = content.replace("<body>", "<body>\n" + BUTTON_HTML)
                
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(new_content)
                    
                print(f"[{i}] {filename}: 🚀 Button Added")
                count += 1
            else:
                print(f"[{i}] {filename}: ⚠️  No <body> tag")
                
        except Exception as e:
            print(f"[{i}] {filename}: ❌ Error {e}")

    print("-" * 30)
    print(f"Done! Added to {count} files. Skipped {skipped} existing.")

if __name__ == "__main__":
    fast_fix()