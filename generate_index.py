import os
import json

folder_path = 'quiz_data'
output_file = 'quiz_manifest.json'
files_data = []

print("Scanning library...")

if os.path.exists(folder_path):
    for root, dirs, filenames in os.walk(folder_path):
        for filename in filenames:
            if filename.endswith('.json'):
                full_path = os.path.join(root, filename)
                try:
                    with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                        data = json.load(f)
                        count = 0
                        if isinstance(data, list): count = len(data)
                        elif isinstance(data, dict) and 'questions' in data: count = len(data['questions'])
                        
                        files_data.append({ "file": filename, "count": count })
                except: pass

    with open(output_file, 'w') as f:
        json.dump(files_data, f)
        
    print(f"✅ Indexed {len(files_data)} Q-Banks successfully.")
else:
    print(f"❌ Error: '{folder_path}' folder not found.")