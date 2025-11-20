import os
import traceback

# --- CONFIGURATION ---
HTML_FILE = "resources.html"
MATERIALS_FOLDER = "materials"

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

def generate_card(filename, icon, tag):
    display_name = filename.replace(".pdf", "").replace("_", " ").title()
    unique_id = filename.replace(" ", "_").replace(".", "_")
    
    return f"""
    <div class="resource-card">
        <div class="check-circle" data-id="{unique_id}" onclick="toggleRead(this, '{unique_id}')"></div>
        <a href="{MATERIALS_FOLDER}/{filename}#toolbar=0&navpanes=0" target="_blank" style="text-decoration: none; color: inherit; display: flex; flex-grow: 1; align-items: center; gap: 15px;">
            <div class="icon-box">{icon}</div>
            <div class="card-info">
                <div class="card-title">{display_name}</div>
                <div class="card-desc">Click to open resource.</div>
                <span class="tag">{tag}</span>
            </div>
        </a>
    </div>
    """

def update_resources():
    print("--- MEDTRIX RESOURCE UPDATER (v2) ---")
    
    if not os.path.exists(MATERIALS_FOLDER):
        print(f"Error: '{MATERIALS_FOLDER}' folder missing!")
        return

    # 1. Scan Files
    files = [f for f in os.listdir(MATERIALS_FOLDER) if f.lower().endswith('.pdf')]
    files.sort()
    print(f"Scanning {len(files)} files...")

    # 2. Categorize
    grouped_files = {}
    for f in files:
        lower_name = f.lower()
        found_match = False
        for key, data in SUBJECT_MAP.items():
            if key in lower_name:
                subject = data['title']
                icon = data['icon']
                if subject not in grouped_files: grouped_files[subject] = {"icon": icon, "files": []}
                grouped_files[subject]["files"].append(f)
                found_match = True
                break
        if not found_match:
            subject = DEFAULT_CAT['title']
            if subject not in grouped_files: grouped_files[subject] = {"icon": DEFAULT_CAT['icon'], "files": []}
            grouped_files[subject]["files"].append(f)

    # 3. Build HTML Content
    new_html_content = ""
    for subject in sorted(grouped_files.keys()):
        data = grouped_files[subject]
        icon = data['icon']
        # Header
        new_html_content += f"""
    <div style="grid-column: 1 / -1; margin-top: 30px; border-bottom: 2px solid var(--border); padding-bottom: 10px; color: var(--accent); font-weight: bold; font-size: 1.2rem; display: flex; align-items: center; gap: 10px;">
        <span>{icon}</span> {subject}
    </div>
    """
        # Cards
        for filename in data['files']:
            short_tag = subject.split()[0]
            new_html_content += generate_card(filename, icon, short_tag)

    # 4. Inject into File (Safer Method)
    try:
        with open(HTML_FILE, "r", encoding="utf-8") as f:
            full_html = f.read()
            
        start_marker = ""
        end_marker = ""
        
        # Use find() instead of split() to avoid "empty separator" errors
        start_idx = full_html.find(start_marker)
        end_idx = full_html.find(end_marker)
        
        if start_idx == -1 or end_idx == -1:
            print("❌ ERROR: Markers not found in HTML file!")
            print(f"Please paste these markers inside {HTML_FILE}:")
            print(f"{start_marker}\n{end_marker}")
            return

        # Slice the string safely
        before = full_html[:start_idx + len(start_marker)]
        after = full_html[end_idx:]
        
        updated_html = before + "\n" + new_html_content + "\n    " + after
        
        with open(HTML_FILE, "w", encoding="utf-8") as f:
            f.write(updated_html)
            
        print(f"✅ Success! Resources updated.")
        
    except Exception:
        print("❌ CRITICAL ERROR:")
        traceback.print_exc()

if __name__ == "__main__":
    update_resources()