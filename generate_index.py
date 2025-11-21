import os
import json

# Path to your data folder
folder_path = 'quiz_data'
output_file = 'quiz_manifest.json'

files = []

# Scan the directory
if os.path.exists(folder_path):
    for filename in os.listdir(folder_path):
        if filename.endswith('.json'):
            files.append(filename)
            
    # Save the list to a JSON file
    with open(output_file, 'w') as f:
        json.dump(files, f)
        
    print(f"Success! Found {len(files)} files. Saved list to {output_file}")
else:
    print(f"Error: Folder '{folder_path}' not found.")