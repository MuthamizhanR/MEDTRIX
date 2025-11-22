import os
import json
import re

folder_path = 'quiz_data'
output_file = 'quiz_manifest.json'
files_data = []

# Categories mapping
CATEGORIES = {
    "Previous Year Papers": ["neet", "inicet", "fmge", "pyq", "aiims", "jipmer"],
    "Grand Tests": ["grand", "gt", "mock"],
    "Anatomy": ["anat"],
    "Physiology": ["physio"],
    "Biochemistry": ["biochem"],
    "Pathology": ["patho"],
    "Pharmacology": ["pharm"],
    "Microbiology": ["micro"],
    "Forensic Medicine": ["fmt", "forensic"],
    "Community Medicine": ["psm", "community"],
    "ENT": ["ent"],
    "Ophthalmology": ["eye", "opthal"],
    "Medicine": ["med"],
    "Surgery": ["surg"],
    "Obstetrics": ["obg", "gyn"],
    "Pediatrics": ["pedia"],
    "Orthopedics": ["ortho"],
    "Dermatology": ["derma", "skin"],
    "Psychiatry": ["psych"],
    "Radiology": ["radio"],
    "Anesthesia": ["anesth"]
}

print(f"📂 Scanning '{folder_path}'...")

if os.path.exists(folder_path):
    total_files_seen = 0
    
    for root, dirs, filenames in os.walk(folder_path):
        for filename in filenames:
            # Check for json (case insensitive)
            if filename.lower().endswith('.json'):
                total_files_seen += 1
                full_path = os.path.join(root, filename)
                
                try:
                    with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                        data = json.load(f)
                        
                        # Count questions
                        count = 0
                        if isinstance(data, list): count = len(data)
                        elif isinstance(data, dict) and 'questions' in data: count = len(data['questions'])
                        
                        # 1. Categorize
                        cat = "Uncategorized"
                        lower_name = filename.lower()
                        for c, keys in CATEGORIES.items():
                            if any(k in lower_name for k in keys):
                                cat = c
                                break
                        
                        # 2. Format Title (THE FIX IS HERE: [_\-\s])
                        # Removes leading numbers like "01_", "272-", etc.
                        clean_name = filename.replace('.json', '').replace('.JSON', '')
                        title = re.sub(r'^\d+[_\-\s]*', '', clean_name)
                        title = title.replace('_', ' ').replace('-', ' ').title()

                        files_data.append({
                            "file": filename,
                            "title": title,
                            "category": cat,
                            "count": count
                        })
                        
                except Exception as e:
                    print(f"  ⚠️ Skipping {filename}: {e}")

    # Save manifest
    if len(files_data) > 0:
        # Sort by Category, then Title
        files_data.sort(key=lambda x: (x['category'], x['title']))
        
        with open(output_file, 'w') as f:
            json.dump(files_data, f)
        print(f"\n✅ SUCCESS! Indexed {len(files_data)} tests.")
    else:
        print(f"\n❌ Found {total_files_seen} JSON files, but failed to index them.")

else:
    print(f"❌ Error: Folder '{folder_path}' not found.")