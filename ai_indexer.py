import os
import json
import time
import requests

# --- CONFIGURATION ---
FOLDER_PATH = 'quiz_data'
OUTPUT_FILE = 'quiz_manifest.json'
API_KEY = "AIzaSyAvG61ZVSmjer_PNsixRsxxqf7gaoNz7nQ"  # Your Key
BATCH_SIZE = 30  # How many files to ask AI about at once

# Standard MBBS Subjects for AI to choose from
SUBJECTS = [
    "Anatomy", "Physiology", "Biochemistry", "Pathology", "Pharmacology", 
    "Microbiology", "Forensic Medicine", "Community Medicine", "ENT", 
    "Ophthalmology", "Medicine", "Surgery", "Obstetrics & Gynaecology", 
    "Pediatrics", "Orthopedics", "Dermatology", "Psychiatry", 
    "Radiology", "Anesthesia", "Previous Year Papers", "Grand Tests"
]

def format_title(filename):
    # Clean up filename for display
    name = filename.replace('.json', '')
    # Remove leading numbers/underscores
    import re
    name = re.sub(r'^\d+[_-\s]*', '', name)
    name = name.replace('_', ' ').replace('-', ' ')
    return name.title()

def get_ai_classification(filenames):
    """Sends a batch of filenames to Gemini to categorize."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
    
    prompt = f"""
    You are a medical librarian. I will give you a list of filenames containing medical quiz questions.
    Classify each file into ONE of these exact subjects: {json.dumps(SUBJECTS)}.
    
    Rules:
    1. If it mentions "Labor", "Pregnancy", "Uterus", it is "Obstetrics & Gynaecology".
    2. If it mentions "Fracture", "Bone", it is "Orthopedics".
    3. If it mentions "Diabetes" check context: if pregnancy -> OBG, if drug -> Pharma, else Medicine.
    4. If it mentions "NEET", "INICET", "Recall", "PYQ", it is "Previous Year Papers".
    5. If uncertain, use "General Medicine".
    
    Input Files:
    {json.dumps(filenames)}
    
    Output format: JSON object where key is filename and value is the Category.
    Example: {{ "diabetes_pregnancy.json": "Obstetrics & Gynaecology" }}
    Do not use Markdown formatting. Just raw JSON.
    """
    
    payload = {
        "contents": [{ "parts": [{ "text": prompt }] }]
    }
    
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            raw_text = response.json()['candidates'][0]['content']['parts'][0]['text']
            # Clean up markdown if AI adds it
            raw_text = raw_text.replace('```json', '').replace('```', '').strip()
            return json.loads(raw_text)
        else:
            print(f"  ⚠️ AI Error {response.status_code}: {response.text}")
            return {}
    except Exception as e:
        print(f"  ⚠️ Connection Error: {e}")
        return {}

def main():
    print("🚀 Starting AI Sort... This handles the logic you asked for.")
    
    all_files = []
    files_to_process = []
    
    # 1. Scan Files
    if os.path.exists(FOLDER_PATH):
        for root, dirs, filenames in os.walk(FOLDER_PATH):
            for filename in filenames:
                if filename.lower().endswith('.json'):
                    # Quick Pre-Check (Save AI tokens for obvious ones)
                    cat = "Unknown"
                    lower = filename.lower()
                    
                    # Simple keywords to skip AI if obvious
                    if "anat" in lower: cat = "Anatomy"
                    elif "surg" in lower and "neuro" not in lower: cat = "Surgery"
                    elif "patho" in lower: cat = "Pathology"
                    elif "pharm" in lower: cat = "Pharmacology"
                    elif "psm" in lower: cat = "Community Medicine"
                    elif "ent" in lower: cat = "ENT"
                    elif "opthal" in lower or "eye" in lower: cat = "Ophthalmology"
                    elif "forensic" in lower or "fmt" in lower: cat = "Forensic Medicine"
                    
                    full_path = os.path.join(root, filename)
                    
                    # Get Question Count
                    count = 0
                    try:
                        with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                            data = json.load(f)
                            if isinstance(data, list): count = len(data)
                            elif isinstance(data, dict) and 'questions' in data: count = len(data['questions'])
                    except: pass

                    file_obj = {
                        "file": filename,
                        "title": format_title(filename),
                        "count": count,
                        "category": cat
                    }
                    
                    all_files.append(file_obj)
                    
                    # If simple check failed, add to AI queue
                    if cat == "Unknown":
                        files_to_process.append(filename)
    
    # 2. Process with AI in Batches
    total_batches = (len(files_to_process) // BATCH_SIZE) + 1
    print(f"🧠 AI Analysis: {len(files_to_process)} tricky files found. Processing in {total_batches} batches...")
    
    ai_results = {}
    
    for i in range(0, len(files_to_process), BATCH_SIZE):
        batch = files_to_process[i:i+BATCH_SIZE]
        print(f"  - Batch {i//BATCH_SIZE + 1}/{total_batches} ({len(batch)} files)...", end="\r")
        
        results = get_ai_classification(batch)
        ai_results.update(results)
        time.sleep(1) # Respect API limits
        
    print("\n✅ AI Processing Complete.")

    # 3. Merge Results
    final_data = []
    for item in all_files:
        if item["category"] == "Unknown":
            # Use AI result, default to Medicine if AI failed
            item["category"] = ai_results.get(item["file"], "General Medicine")
        final_data.append(item)

    # 4. Sort & Save
    final_data.sort(key=lambda x: (x['category'], x['title']))
    
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(final_data, f)
        
    print(f"🎉 Database Updated! {len(final_data)} tests organized into subjects.")

if __name__ == "__main__":
    main()