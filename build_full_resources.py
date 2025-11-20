import os
import datetime

# --- CONFIGURATION ---
MATERIALS_FOLDER = "materials"
HTML_OUTPUT = "resources.html"

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
HTML_HEAD = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MEDTRIX | Study Resources</title>
    <style>
        :root {
            --primary: #0056b3; --accent: #00a8cc; --bg: #f4f7f6;
            --card-bg: #ffffff; --text: #333; --header-text: #fff;
            --shadow: rgba(0,0,0,0.1); --brand-color: #00e5ff;
            --border: #e0e0e0;
        }
        [data-theme="dark"] {
            --primary: #1a1a1a; --accent: #bb86fc; --bg: #121212;
            --card-bg: #1e1e1e; --text: #e0e0e0; --header-text: #e0e0e0;
            --shadow: rgba(0,0,0,0.5); --brand-color: #ffffff;
            --border: #333;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', sans-serif; }
        body { background: var(--bg); color: var(--text); transition: 0.3s; padding-bottom: 60px; }

        /* HEADER */
        header {
            background: linear-gradient(135deg, var(--primary), var(--accent));
            padding: 20px; color: var(--header-text);
            display: flex; align-items: center; justify-content: space-between;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2); position: sticky; top: 0; z-index: 1000;
        }
        .brand { font-family: 'Verdana', sans-serif; font-weight: bold; font-size: 1.2rem; text-transform: uppercase; color: var(--brand-color); text-decoration: none; }

        /* SEARCH BAR */
        .search-container { max-width: 1200px; margin: 20px auto 10px; padding: 0 20px; }
        #searchInput {
            width: 100%; padding: 15px 20px; border-radius: 30px; border: none;
            background: var(--card-bg); color: var(--text); font-size: 1rem;
            box-shadow: 0 4px 10px var(--shadow); outline: none; transition: 0.3s;
        }
        #searchInput:focus { box-shadow: 0 0 15px var(--accent); transform: scale(1.01); }

        /* ACCORDION & GRID SYSTEM */
        .subject-group { max-width: 1200px; margin: 20px auto; padding: 0 20px; animation: fadeIn 0.5s ease forwards; }
        
        .subject-header {
            display: flex; align-items: center; gap: 10px; cursor: pointer;
            padding: 15px; background: var(--card-bg); border-radius: 12px;
            margin-bottom: 15px; box-shadow: 0 2px 5px var(--shadow);
            transition: 0.2s; user-select: none; border-left: 5px solid var(--accent);
        }
        .subject-header:hover { transform: translateX(5px); background: var(--bg); }
        .subject-title { font-size: 1.2rem; font-weight: bold; flex-grow: 1; }
        .toggle-icon { transition: transform 0.3s; }
        .collapsed .toggle-icon { transform: rotate(-90deg); }
        
        .resource-grid {
            display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 15px; margin-bottom: 30px;
            transition: max-height 0.3s ease-out, opacity 0.3s ease-out;
            max-height: 2000px; opacity: 1; overflow: hidden;
        }
        .collapsed + .resource-grid { max-height: 0; opacity: 0; margin-bottom: 0; }

        /* CARDS */
        .resource-card {
            background: var(--card-bg); border-radius: 15px; border: 1px solid var(--border);
            padding: 20px; display: flex; align-items: center; gap: 15px;
            text-decoration: none; color: var(--text); transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative; overflow: hidden;
        }
        .resource-card:hover { transform: translateY(-5px) scale(1.02); box-shadow: 0 10px 20px var(--shadow); border-color: var(--accent); }
        .resource-card::before {
            content: ''; position: absolute; top: 0; left: 0; width: 4px; height: 100%;
            background: var(--accent); opacity: 0; transition: 0.3s;
        }
        .resource-card:hover::before { opacity: 1; }

        .icon-box { font-size: 1.8rem; }
        .card-info { flex-grow: 1; }
        .card-title { font-weight: bold; font-size: 1rem; margin-bottom: 4px; line-height: 1.2; }
        .card-desc { font-size: 0.8rem; opacity: 0.7; }
        
        /* CHECKBOX */
        .check-circle {
            width: 22px; height: 22px; border: 2px solid var(--text); border-radius: 50%;
            cursor: pointer; display: flex; align-items: center; justify-content: center;
            transition: 0.2s; opacity: 0.3; z-index: 10;
        }
        .check-circle:hover { opacity: 1; border-color: var(--accent); }
        .check-circle.checked { background: #28a745; border-color: #28a745; opacity: 1; color: white; }
        .check-circle.checked::after { content: '✓'; font-size: 12px; font-weight: bold; }

        /* ANIMATIONS */
        @keyframes fadeIn { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: 0; } }
    </style>
</head>
<body>

<header>
    <a href="index.html" class="brand">← Back to Home</a>
    <div style="font-size:0.9rem; opacity:0.8">Library</div>
</header>

<div class="search-container">
    <input type="text" id="searchInput" onkeyup="filterContent()" placeholder="🔍 Search notes, topics, or subjects...">
</div>

<div id="main-content">
"""

HTML_FOOTER = """
</div>

<script>
    // 1. Theme Logic
    if(localStorage.getItem('medtrix-theme') === 'dark') {
        document.documentElement.setAttribute('data-theme', 'dark');
    }

    // 2. Accordion Logic
    function toggleSection(header) {
        header.classList.toggle('collapsed');
    }

    // 3. Checkbox Logic
    function toggleRead(btn, id, e) {
        e.preventDefault(); // Prevent link click
        e.stopPropagation();
        btn.classList.toggle('checked');
        if (btn.classList.contains('checked')) {
            localStorage.setItem('read_' + id, 'true');
        } else {
            localStorage.removeItem('read_' + id);
        }
    }

    // 4. Restore Progress
    window.addEventListener('load', function() {
        const checks = document.querySelectorAll('.check-circle');
        checks.forEach(check => {
            const id = check.getAttribute('data-id');
            if (localStorage.getItem('read_' + id) === 'true') {
                check.classList.add('checked');
            }
        });
    });

    // 5. Search Logic
    function filterContent() {
        let input = document.getElementById('searchInput').value.toLowerCase();
        let groups = document.querySelectorAll('.subject-group');

        groups.forEach(group => {
            let cards = group.querySelectorAll('.resource-card');
            let groupVisible = false;

            cards.forEach(card => {
                let text = card.innerText.toLowerCase();
                if (text.includes(input)) {
                    card.style.display = "flex";
                    groupVisible = true;
                } else {
                    card.style.display = "none";
                }
            });

            // Hide entire subject group if no cards match
            if(groupVisible) {
                group.style.display = "block";
                // Auto-expand when searching
                if(input.length > 0) {
                    group.querySelector('.subject-header').classList.remove('collapsed');
                }
            } else {
                group.style.display = "none";
            }
        });
    }
</script>
</body>
</html>
"""

def generate_full_site():
    print("--- BUILDING RESOURCES PAGE ---")
    
    if not os.path.exists(MATERIALS_FOLDER):
        print(f"❌ Error: '{MATERIALS_FOLDER}' folder not found.")
        return

    # 1. Scan Files
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

    # 3. Build Content HTML
    content_html = ""
    
    for subject in sorted(grouped.keys()):
        data = grouped[subject]
        files = data['files']
        icon = data['icon']
        
        # Create the Section Header (Accordion)
        content_html += f"""
        <div class="subject-group">
            <div class="subject-header" onclick="toggleSection(this)">
                <div class="icon-box">{icon}</div>
                <div class="subject-title">{subject} <span style="font-size:0.8rem; opacity:0.6; font-weight:normal">({len(files)})</span></div>
                <div class="toggle-icon">▼</div>
            </div>
            <div class="resource-grid">
        """
        
        # Create the Cards (Tiles)
        for f in files:
            clean_name = f.replace('.pdf','').replace('_',' ').title()
            unique_id = f.replace(' ','_').replace('.','_')
            # Tool bar hidden link
            link = f"{MATERIALS_FOLDER}/{f}#toolbar=0&navpanes=0"
            
            content_html += f"""
                <a href="{link}" class="resource-card" target="_blank">
                    <div class="check-circle" data-id="{unique_id}" onclick="toggleRead(this, '{unique_id}', event)"></div>
                    <div class="card-info">
                        <div class="card-title">{clean_name}</div>
                        <div class="card-desc">View PDF Document</div>
                    </div>
                </a>
            """
        
        content_html += """
            </div>
        </div>
        """

    # 4. Combine and Save
    full_html = HTML_HEAD + content_html + HTML_FOOTER
    
    with open(HTML_OUTPUT, 'w', encoding='utf-8') as f:
        f.write(full_html)
        
    print(f"✅ Successfully built {HTML_OUTPUT} with {len(files)} files.")
    print("Features: Grid Layout, Search, Accordions, Animations, Checkboxes.")

if __name__ == "__main__":
    generate_full_site()