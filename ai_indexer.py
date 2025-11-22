import os
import json
import time
import requests
import re

# --- CONFIGURATION ---
FOLDER_PATH = 'quiz_data'
OUTPUT_FILE = 'quiz_manifest.json'
BATCH_SIZE = 30 

# Ask for Key (SECURE WAY - No hardcoding)
print("------------------------------------------------")
print("🔑 ENTER YOUR GOOGLE API KEY TO START SORTING")
print("(The key will not be saved in this file)")
print("------------------------------------------------")
API_KEY = input("API KEY: ").strip()

# Standard MBBS Subjects
SUBJECTS = [
    "Anatomy", "Physiology", "Biochemistry", "Pathology", "Pharmacology", 
    "Microbiology", "Forensic Medicine", "Community Medicine", "ENT", 
    "Ophthalmology", "Medicine", "Surgery", "Obstetrics & Gynaecology", 
    "Pediatrics", "Orthopedics", "Dermatology", "Psychiatry", 
    "Radiology", "Anesthesia", "Previous Year Papers", "Grand Tests"
]

def format_title(filename):
    name = filename.replace('.json', '')
    # FIX: Hyphen moved to the end of the class [_\s-] to prevent Regex Error
    name = re.sub(r'^\d+[_\s-]*', '', name)
    name = name.replace('_', ' ').replace('-', ' ')
    return name.title()

def get_ai_classification(filenames):
    # KEPT gemini-2.0-flash as requested
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"
    
    prompt = f"""
    Classify these medical quiz filenames into ONE of these subjects: {json.dumps(SUBJECTS)}.
    Return strictly JSON key-value pairs.
    Rules:
    - 'GT', 'Grand Test' -> Grand Tests
    - 'PYQ', 'Recall', '2023', '2024' -> Previous Year Papers
    - 'Labor', 'Pregnancy' -> Obstetrics & Gynaecology
    - 'Fracture', 'Bone' -> Orthopedics
    
    Filenames: {json.dumps(filenames)}
    """
    
    payload = { "contents": [{ "parts": [{ "text": prompt }] }] }
    
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            raw = response.json()['candidates'][0]['content']['parts'][0]['text']
            
            # 2.0 Flash often adds markdown, strip it out to prevent crash
            raw = raw.replace('```json', '').replace('```', '').strip()
            
            # Extra Safety: Find the first { and last }
            start = raw.find('{')
            end = raw.rfind('}') + 1
            if start != -1 and end != -1:
                raw = raw[start:end]
                
            return json.loads(raw)
        else:
            print(f"  ⚠️ API Error: {response.status_code}")
            return {}
    except Exception as e:
        print(f"  ⚠️ Parse Error: {e}")
        return {}

def main():
    if not API_KEY or len(API_KEY) < 10:
        print("❌ Invalid Key. Exiting.")
        return

    print("🚀 Starting AI Indexer (Gemini 2.0 Flash)...")
    all_files = []
    files_to_process = []
    
    if os.path.exists(FOLDER_PATH):
        for root, dirs, filenames in os.walk(FOLDER_PATH):
            for filename in filenames:
                if filename.lower().endswith('.json'):
                    # Fast Keyword Check (Save AI tokens)
                    cat = "Unknown"
                    lower = filename.lower()
                    if "anat" in lower: cat = "Anatomy"
                    elif "surg" in lower: cat = "Surgery"
                    elif "patho" in lower: cat = "Pathology"
                    elif "pharm" in lower: cat = "Pharmacology"
                    elif "ent" in lower: cat = "ENT"
                    elif "opthal" in lower or "eye" in lower: cat = "Ophthalmology"
                    elif "forensic" in lower: cat = "Forensic Medicine"
                    elif "psm" in lower: cat = "Community Medicine"
                    elif "med" in lower and "for" not in lower: cat = "Medicine"
                    
                    full_path = os.path.join(root, filename)
                    count = 0
                    try:
                        with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                            data = json.load(f)
                            if isinstance(data, list): count = len(data)
                            elif isinstance(data, dict) and 'questions' in data: count = len(data['questions'])
                    except: pass

                    obj = { "file": filename, "title": format_title(filename), "count": count, "category": cat }
                    all_files.append(obj)
                    if cat == "Unknown": files_to_process.append(filename)
    
    # AI Batch Processing
    if files_to_process:
        print(f"🧠 AI Analyzing {len(files_to_process)} tricky filenames...")
        ai_results = {}
        
        # Process in chunks
        for i in range(0, len(files_to_process), BATCH_SIZE):
            batch = files_to_process[i:i+BATCH_SIZE]
            print(f"  - Processing Batch {i//BATCH_SIZE + 1}...", end="\r")
            
            results = get_ai_classification(batch)
            ai_results.update(results)
            time.sleep(1) # Be nice to the API

        print("\n  ✅ AI Analysis Complete.")

        # Merge Results
        for item in all_files:
            if item["category"] == "Unknown":
                # Fallback to Medicine if AI failed specifically for this file
                item["category"] = ai_results.get(item["file"], "Medicine")

    # Save
    all_files.sort(key=lambda x: (x['category'], x['title']))
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(all_files, f, indent=2)
        
    print(f"🎉 Manifest updated! Saved {len(all_files)} files to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()