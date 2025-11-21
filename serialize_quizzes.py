import os
import json
import re
import hashlib
import html
from bs4 import BeautifulSoup

# --- CONFIGURATION ---
ROOT_DIR = "."  
OUTPUT_DIR = "quiz_data"
MANIFEST_FILE = "manifest.json"
EXCLUDE_FILES = ["qbanks.html", "index.html"]

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

def clean_text_content(text):
    """Removes unwanted signatures and cleans HTML."""
    if not text: return ""
    # Remove specific telegram handle and common variations
    text = text.replace("@dams_new_robot", "")
    text = re.sub(r'@\w+', '', text) # Remove any @mentions
    text = re.sub(r't\.me\/\w+', '', text) # Remove links
    return text.strip()

def categorize_test(title):
    t = title.lower()
    if "cereb" in t or "btr" in t: return "Cerebellum / BTR"
    if "prep" in t or "rr" in t or "rapid" in t: return "Prepladder / RR"
    if "dams" in t or "dqb" in t: return "DAMS / DQB"
    if "aiims" in t: return "AIIMS PYQ"
    if "inicet" in t: return "INICET PYQ"
    if "neet" in t: return "NEET PG PYQ"
    return "Subject Wise / Mixed"

def generate_question_id(text):
    hash_object = hashlib.md5(text.strip().encode('utf-8'))
    return hash_object.hexdigest()[:8]

def clean_filename(text):
    safe_text = re.sub(r'[^\w\s-]', '', text)
    return safe_text.strip().replace(" ", "_")

def extract_from_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except Exception as e:
        print(f"Skipping {filepath}: {e}")
        return []

    soup = BeautifulSoup(content, 'html.parser')
    
    titles_map = {}
    buttons = soup.select('.nav-buttons button')
    for btn in buttons:
        onclick = btn.get('onclick', '')
        match = re.search(r"showTest\('([^']+)'\)", onclick)
        if match:
            titles_map[match.group(1)] = btn.text.strip()

    extracted_entries = []
    containers = soup.select('.iframe-container')
    
    for container in containers:
        container_id = container.get('id')
        title = titles_map.get(container_id)
        if not title:
            h2 = container.find('h2')
            title = h2.text.strip() if h2 else f"Test {container_id}"

        iframe = container.find('iframe')
        if iframe and iframe.get('srcdoc'):
            srcdoc = html.unescape(iframe['srcdoc'])
            json_match = re.search(r'questions\s*=\s*(\[\{.*\}\]);', srcdoc, re.DOTALL)
            
            if json_match:
                try:
                    questions_data = json.loads(json_match.group(1))
                    
                    # --- CLEAN AND PROCESS ---
                    for q in questions_data:
                        q['text'] = clean_text_content(q.get('text', ''))
                        q['explanation'] = clean_text_content(q.get('explanation', ''))
                        q['uid'] = generate_question_id(q['text'])
                        
                        # Ensure fields exist
                        if 'video' not in q: q['video'] = ""
                        if 'audio' not in q: q['audio'] = ""
                        if 'question_images' not in q: q['question_images'] = []
                        if 'explanation_images' not in q: q['explanation_images'] = []
                    
                    safe_title = clean_filename(title)
                    category = categorize_test(title)
                    out_filename = f"{safe_title}.json"
                    
                    counter = 1
                    while os.path.exists(os.path.join(OUTPUT_DIR, out_filename)):
                         out_filename = f"{safe_title}_{counter}.json"
                         counter += 1

                    final_data = {
                        "meta": {
                            "id": container_id,
                            "title": title,
                            "category": category
                        },
                        "questions": questions_data
                    }
                    
                    with open(os.path.join(OUTPUT_DIR, out_filename), 'w', encoding='utf-8') as outfile:
                        json.dump(final_data, outfile, indent=2)
                    
                    extracted_entries.append({
                        "title": title,
                        "category": category,
                        "file": out_filename,
                        "questions": len(questions_data)
                    })
                    
                except json.JSONDecodeError:
                    print(f"Error parsing JSON in {title}")
    
    return extracted_entries

def main():
    all_quizzes = []
    print("Starting extraction & cleaning...")

    for root, dirs, files in os.walk(ROOT_DIR):
        if OUTPUT_DIR in root: continue

        for file in files:
            if file.endswith(".html") and file not in EXCLUDE_FILES:
                full_path = os.path.join(root, file)
                tests = extract_from_file(full_path)
                if tests:
                    all_quizzes.extend(tests)

    # Sort by Category, then Title
    all_quizzes.sort(key=lambda x: (x['category'], x['title']))

    with open(MANIFEST_FILE, "w", encoding='utf-8') as f:
        json.dump(all_quizzes, f, indent=2)

    print(f"\nDONE! Processed {len(all_quizzes)} tests.")

if __name__ == "__main__":
    main()