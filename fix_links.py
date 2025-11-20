import re

TARGET_FILE = "index.html"

def fix_links():
    print("--- FIXING HOME PAGE LINKS ---")
    
    try:
        with open(TARGET_FILE, "r", encoding="utf-8") as f:
            content = f.read()

        # 1. Fix Study Resources (Look for Book Icon 📚)
        # Forces it to go to resources.html
        content = re.sub(
            r'<a href="[^"]*"\s+class="menu-card">\s*<div class="icon">📚</div>', 
            r'<a href="resources.html" class="menu-card">\n            <div class="icon">📚</div>', 
            content
        )
        print("✅ Study Resources (📚) -> Linked to resources.html")

        # 2. Fix Analytics (Look for Chart Icon 📊)
        # Forces it to go to analytics.html
        content = re.sub(
            r'<a href="[^"]*"\s+class="menu-card">\s*<div class="icon">📊</div>', 
            r'<a href="analytics.html" class="menu-card">\n            <div class="icon">📊</div>', 
            content
        )
        print("✅ Analytics (📊) -> Linked to analytics.html")

        # 3. Fix Q-Banks (Look for Stethoscope Icon 🩺)
        # Forces it to go to qbanks.html
        content = re.sub(
            r'<a href="[^"]*"\s+class="menu-card">\s*<div class="icon">🩺</div>', 
            r'<a href="qbanks.html" class="menu-card">\n            <div class="icon">🩺</div>', 
            content
        )
        print("✅ Q-Banks (🩺) -> Linked to qbanks.html")
        
        # 4. Fix Spaced Revision (Look for Brain Icon 🧠)
        # Forces it to go to revision.html
        content = re.sub(
            r'<a href="[^"]*"\s+class="menu-card">\s*<div class="icon">🧠</div>', 
            r'<a href="revision.html" class="menu-card">\n            <div class="icon">🧠</div>', 
            content
        )
        print("✅ Smart Revision (🧠) -> Linked to revision.html")

        with open(TARGET_FILE, "w", encoding="utf-8") as f:
            f.write(content)
            
        print("-" * 30)
        print("🎉 All links repaired successfully!")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    fix_links()