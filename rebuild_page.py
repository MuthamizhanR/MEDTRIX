import os
import urllib.parse

# --- CONFIGURATION ---
OUTPUT_FILE = "resources.html"
MATERIALS_FOLDER = "materials"

# Subject Categories
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
DEFAULT_CAT = {"icon": "📄", "title": "General / Miscellaneous"}

# --- HTML TEMPLATE PARTS ---
HTML_TOP = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MEDTRIX | Library</title>
    <style>
        :root { --primary: #0056b3; --accent: #00a8cc; --bg: #f4f7f6; --card-bg: #ffffff; --text: #333; --border: #e0e0e0; }
        [data-theme="dark"] { --primary: #1a1a1a; --accent: #bb86fc; --bg: #121212; --card-bg: #1e1e1e; --text: #e0e0e0; --border: #333; }

        body { margin: 0; padding: 0; font-family: 'Segoe UI', sans-serif; background: var(--bg); color: var(--text); padding-bottom: 60px; }

        /* HEADER */
        header {
            background: linear-gradient(135deg, var(--primary), var(--accent));
            padding: 20px; color: white; display: flex; align-items: center; justify-content: space-between;
            position: sticky; top: 0; z-index: 1000; box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        }
        .brand { font-weight: bold; font-size: 1.2rem; color: white; text-decoration: none; }

        /* CONTROLS */
        .controls { padding: 20px; max-width: 1200px; margin: 0 auto; }
        #searchInput {
            width: 100%; padding: 15px; border-radius: 30px; border: none;
            background: var(--card-bg); color: var(--text); box-shadow: 0 4px 10px rgba(0,0,0,0.05);
            font-size: 1rem; outline: none;
        }

        /* CONTENT LAYOUT */
        .main-container { max-width: 1200px; margin: 0 auto; padding: 0 20px; }
        .subject-group { margin-bottom: 30px; animation: fadeIn 0.5s ease; }
        
        .subject-header {
            font-size: 1.3rem; font-weight: bold; color: var(--accent);
            padding: 10px 0; border-bottom: 2px solid var(--border); margin-bottom: 15px;
            display: flex; align-items: center; gap: 10px; cursor: pointer;
        }
        .subject-header:hover { opacity: 0.8; }
        
        .resource-grid {
            display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 15px;
        }
        .subject-header.collapsed + .resource-grid { display: none; }
        .subject-header.collapsed .toggle-icon { transform: rotate(-90deg); }
        .toggle-icon { transition: 0.3s; font-size: 0.8rem; margin-left: 10px; }

        /* CARDS */
        .resource-card {
            background: var(--card-bg); border-radius: 12px; padding: 20px;
            border: 1px solid var(--border); display: flex; align-items: center; gap: 15px;
            text-decoration: none; color: var(--text); transition: 0.2s;
        }
        .resource-card:hover { transform: translateY(-5px); border-color: var(--accent); box-shadow: 0 5px 15px rgba(0,0,0,0.1); }

        .check-circle {
            width: 24px; height: 24px; border: 2px solid var(--text); border-radius: 50%; opacity: 0.3;
            display: flex; align-items: center; justify-content: center; cursor: pointer;
        }
        .check-circle:hover { opacity: 1; border-color: var(--accent); }
        .check-circle.checked { background: #28a745; border-color: #28a745; color: white; opacity: 1; }
        .check-circle.checked::after { content: '✓'; font-weight: bold; }

        .card-info { flex-grow: 1; }
        .card-title { font-weight: bold; font-size: 1rem; margin-bottom: 5px; }
        .card-desc { font-size: 0.8rem; opacity: 0.6; }

        @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: 0; } }
    </style>
</head>
<body>

<header>
    <a href="index.html" class="brand">← Back to Home</a>
    <div>Library</div>
</header>

<div class="controls">
    <input type="text" id="searchInput" onkeyup="filterContent()" placeholder="🔍 Search your notes...">
</div>

<div class="main-container">
"""

HTML_BOTTOM = """
</div>

<script>
    if(localStorage.getItem('medtrix-theme') === 'dark') document.documentElement.setAttribute('data-theme', 'dark');

    function toggleSection(header) {
        header.classList.toggle('collapsed');
    }

    function toggleRead(btn, id, e) {
        e.preventDefault(); e.stopPropagation();
        btn.classList.toggle('checked');
        if(btn.classList.contains('checked')) localStorage.setItem('read_'+id, 'true');
        else localStorage.removeItem('read_'+id);
    }

    window.addEventListener('load', () => {
        document.querySelectorAll('.check-circle').forEach(btn => {
            if(localStorage.getItem('read_'+btn.getAttribute('data-id')) === 'true') btn.classList.add('checked');
        });
    });

    function filterContent() {
        let term = document.getElementById('searchInput').value.toLowerCase();
        document.querySelectorAll('.subject-group').forEach(group => {
            let hasMatch = false;
            group.querySelectorAll('.resource-card').forEach(card => {
                let text = card.innerText.toLowerCase();
                if(text.includes(term)) { card.style.display = 'flex'; hasMatch = true; }
                else card.style.display = 'none';
            });
            group.style.display = hasMatch ? 'block' : 'none';
            if(term.length > 0 && hasMatch) group.querySelector('.subject-header').classList.remove('collapsed');
        });
    }
</script>
</body>
</html>
"""

def build_page():
    print("--- REBUILDING PAGE FROM SCRATCH ---")
    
    if not os.path.exists(MATERIALS_FOLDER):
        print("Error: Materials folder not found.")
        return

    # 1. Get Files
    files = [f for f in os.listdir(MATERIALS_FOLDER) if f.lower().endswith('.pdf')]
    files.sort()
    
    # 2. Group Files
    grouped = {}
    for f in files:
        lower = f.lower()
        found = False
        for key, val in SUBJECT_MAP.items():
            if key in lower:
                subj = val['title']
                icon = val['icon']
                if subj not in grouped: grouped[subj] = {'icon': icon, 'files': []}
                grouped[subj]['files'].append(f)
                found = True
                break
        if not found:
            subj = DEFAULT_CAT['title']
            if subj not in grouped: grouped[subj] = {'icon': DEFAULT_CAT['icon'], 'files': []}
            grouped[subj]['files'].append(f)

    # 3. Generate Content HTML
    content_html = ""
    for subject in sorted(grouped.keys()):
        data = grouped[subject]
        icon = data['icon']
        
        content_html += f"""
        <div class="subject-group">
            <div class="subject-header" onclick="toggleSection(this)">
                <span>{icon} {subject}</span>
                <span class="toggle-icon">▼</span>
            </div>
            <div class="resource-grid">
        """
        
        for f in data['files']:
            clean_name = f.replace('.pdf','').replace('_',' ').title()
            unique_id = f.replace(' ','_').replace('.','_')
            safe_filename = urllib.parse.quote(f)
            
            content_html += f"""
                <a href="viewer.html?file={safe_filename}" class="resource-card" target="_blank">
                    <div class="check-circle" data-id="{unique_id}" onclick="toggleRead(this, '{unique_id}', event)"></div>
                    <div class="card-info">
                        <div class="card-title">{clean_name}</div>
                        <div class="card-desc">Open Note</div>
                    </div>
                </a>
            """
        content_html += "</div></div>"

    # 4. Write Full File
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(HTML_TOP + content_html + HTML_BOTTOM)

    print(f"✅ REBUILD COMPLETE. Created {OUTPUT_FILE} with {len(files)} files.")

if __name__ == "__main__":
    build_page()