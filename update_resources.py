import os
import urllib.parse

# --- CONFIGURATION ---
MATERIALS_FOLDER = "materials"
OUTPUT_FILE = "resources.html"

# YOUR RICH SUBJECT MAP (Restored)
SUBJECT_MAP = {
    "neuro":    {"icon": "🧠", "title": "Neuroanatomy & Neurology"},
    "cardio":   {"icon": "🫀", "title": "Cardiology"},
    "ortho":    {"icon": "🦴", "title": "Orthopedics"},
    "surg":     {"icon": "✂️", "title": "Surgery"},
    "derma":    {"icon": "🧖", "title": "Dermatology"},
    "pharm":    {"icon": "💊", "title": "Pharmacology"},
    "patho":    {"icon": "🔬", "title": "Pathology"},
    "micro":    {"icon": "🦠", "title": "Microbiology"},
    "pedia":    {"icon": "👶", "title": "Pediatrics"},
    "obs":      {"icon": "🤰", "title": "Obstetrics & Gynaecology"},
    "gyn":      {"icon": "🤰", "title": "Obstetrics & Gynaecology"},
    "ent":      {"icon": "👂", "title": "ENT"},
    "eye":      {"icon": "👁️", "title": "Ophthalmology"},
    "psm":      {"icon": "📈", "title": "PSM / Community Med"},
    "anat":     {"icon": "💀", "title": "General Anatomy"},
    "physio":   {"icon": "⚡", "title": "Physiology"},
    "biochem":  {"icon": "🧪", "title": "Biochemistry"},
    "fmt":      {"icon": "⚖️", "title": "Forensic Medicine"},
}
DEFAULT_CAT = {"icon": "📂", "title": "General / Miscellaneous"}

# --- HTML TEMPLATE ---
HTML_HEADER = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MEDTRIX | Library</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
    <style>
        :root { --bg: #121212; --card: #1e1e1e; --text: #e0e0e0; --accent: #bb86fc; --border: #333; }
        
        body { background-color: var(--bg); color: var(--text); font-family: 'Inter', sans-serif; margin: 0; padding: 20px; padding-bottom: 100px; }
        
        /* HEADER */
        .header { padding-bottom: 20px; border-bottom: 1px solid var(--border); margin-bottom: 30px; }
        .back-btn { text-decoration: none; color: var(--accent); font-weight: 600; display: flex; align-items: center; gap: 8px; font-size: 1.1rem; }
        .back-btn:hover { opacity: 0.8; }

        /* SUBJECT GROUPS */
        .subject-group { margin-bottom: 15px; border: 1px solid var(--border); border-radius: 12px; background: var(--card); overflow: hidden; }
        
        .subject-header {
            padding: 15px 20px; cursor: pointer; display: flex; align-items: center; justify-content: space-between;
            background: rgba(255,255,255,0.03); transition: background 0.2s;
        }
        .subject-header:hover { background: rgba(255,255,255,0.08); }
        
        .header-left { display: flex; align-items: center; gap: 15px; }
        .cat-icon { font-size: 1.5rem; }
        .cat-title { font-weight: 700; font-size: 1.1rem; }
        .count-badge { font-size: 0.8rem; opacity: 0.6; background: rgba(0,0,0,0.3); padding: 2px 8px; border-radius: 10px; margin-left: 8px; }
        
        .toggle-icon { transition: transform 0.3s; opacity: 0.7; }
        .toggle-icon.open { transform: rotate(180deg); }

        /* GRID (Hidden by default) */
        .resource-grid {
            display: none; /* COLLAPSED BY DEFAULT */
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 15px; padding: 20px;
            border-top: 1px solid var(--border);
            animation: slideDown 0.3s ease-out;
        }
        @keyframes slideDown { from { opacity: 0; transform: translateY(-10px); } to { opacity: 1; transform: translateY(0); } }

        /* CARDS */
        .resource-card {
            background: rgba(0,0,0,0.2); border-radius: 10px; padding: 15px;
            display: flex; align-items: center; gap: 15px; border: 1px solid transparent;
            transition: all 0.2s; position: relative;
        }
        .resource-card:hover { border-color: var(--accent); background: rgba(255,255,255,0.05); transform: translateY(-2px); }

        /* CHECK CIRCLE (OVAL FIX) */
        .check-circle {
            width: 24px; height: 24px; border-radius: 50%;
            border: 2px solid #555; cursor: pointer;
            flex-shrink: 0; /* PREVENTS SQUISHING */
            transition: 0.2s;
        }
        .check-circle.read { background: var(--accent); border-color: var(--accent); box-shadow: 0 0 10px var(--accent); }

        /* TEXT CONTENT */
        .card-link { text-decoration: none; color: inherit; flex-grow: 1; display: flex; flex-direction: column; gap: 4px; }
        .card-title { font-weight: 600; line-height: 1.4; font-size: 0.95rem; }
        .card-sub { font-size: 0.75rem; color: #888; }
        
    </style>
</head>
<body>

<div class="header">
    <a href="index.html" class="back-btn"><i class="fas fa-arrow-left"></i> Back to Home</a>
</div>

<div id="library">
"""

def generate_resources():
    print("--- RESTORING RICH CATEGORIES ---")
    
    if not os.path.exists(MATERIALS_FOLDER):
        print(f"Error: '{MATERIALS_FOLDER}' folder missing!")
        return

    files = [f for f in os.listdir(MATERIALS_FOLDER) if f.lower().endswith('.pdf')]
    files.sort()

    # Group files using YOUR Subject Map
    grouped_files = {}
    
    for f in files:
        lower_name = f.lower()
        found = False
        for key, data in SUBJECT_MAP.items():
            if key in lower_name:
                cat_title = data['title']
                if cat_title not in grouped_files: 
                    grouped_files[cat_title] = {'icon': data['icon'], 'files': []}
                grouped_files[cat_title]['files'].append(f)
                found = True
                break
        
        if not found:
            # Default category
            def_title = DEFAULT_CAT['title']
            if def_title not in grouped_files:
                grouped_files[def_title] = {'icon': DEFAULT_CAT['icon'], 'files': []}
            grouped_files[def_title]['files'].append(f)

    # Build HTML
    html = HTML_HEADER
    
    # Sort categories alphabetically
    for category in sorted(grouped_files.keys()):
        data = grouped_files[category]
        safe_id = category.replace(" ", "_").replace("&", "")
        
        html += f"""
        <div class="subject-group">
            <div class="subject-header" onclick="toggleGrid(this)">
                <div class="header-left">
                    <span class="cat-icon">{data['icon']}</span>
                    <span class="cat-title">{category}</span>
                    <span class="count-badge">{len(data['files'])}</span>
                </div>
                <i class="fas fa-chevron-down toggle-icon"></i>
            </div>
            <div class="resource-grid">
        """
        
        for filename in data['files']:
            display_name = filename.replace(".pdf", "").replace("_", " ")
            safe_link = urllib.parse.quote(filename)
            unique_id = filename.replace(" ", "_")
            
            html += f"""
            <div class="resource-card">
                <div class="check-circle" id="check_{unique_id}" onclick="toggleRead(this, '{unique_id}')"></div>
                <a href="viewer.html?file={safe_link}" class="card-link">
                    <div class="card-title">{display_name}</div>
                    <div class="card-sub">Tap to read</div>
                </a>
            </div>
            """
            
        html += "</div></div>"

    html += """
</div>

<script>
    // 1. TOGGLE SECTIONS (Collapsed by Default)
    function toggleGrid(header) {
        const grid = header.nextElementSibling;
        const icon = header.querySelector('.toggle-icon');
        
        if (grid.style.display === 'grid') {
            grid.style.display = 'none';
            icon.classList.remove('open');
        } else {
            grid.style.display = 'grid';
            icon.classList.add('open');
        }
    }

    // 2. READ MARKER (LocalStorage)
    function toggleRead(circle, id) {
        circle.classList.toggle('read');
        const isRead = circle.classList.contains('read');
        if(isRead) localStorage.setItem('read_' + id, 'true');
        else localStorage.removeItem('read_' + id);
    }

    // 3. RESTORE READ STATUS ON LOAD
    document.addEventListener('DOMContentLoaded', () => {
        document.querySelectorAll('.check-circle').forEach(circle => {
            const id = circle.id.replace('check_', '');
            if(localStorage.getItem('read_' + id)) circle.classList.add('read');
        });
    });
</script>
</body>
</html>
"""

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(html)
        
    print(f"✅ Resources Updated! {len(files)} files processed.")
    print("   - Categories: RESTORED")
    print("   - Ovals: FIXED")
    print("   - Toggles: COLLAPSED")

if __name__ == "__main__":
    generate_resources()