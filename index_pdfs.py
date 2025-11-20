import os
import json
from pypdf import PdfReader

MATERIALS_FOLDER = "materials"
OUTPUT_JSON = "pdf_data.json"

# EXTENDED JUNK FILTER
IGNORE_LIST = [
    "telegram", "t.me", "www.", "http", "copyright", "reserved", "page", 
    "uworld", "join", "channel", "subscribe", "medtrix", "downloaded"
]

def is_junk(text):
    text_lower = text.lower().strip()
    if len(text_lower) < 4: return True
    if text_lower.isdigit(): return True
    # Check keywords
    for keyword in IGNORE_LIST:
        if keyword in text_lower:
            return True
    # Check for "Chapter 1" style headers if they are just numbers
    if text_lower.startswith("chapter") and len(text_lower) < 10:
        return False 
    return False

def extract_header(text):
    lines = text.split('\n')
    # Scan top 10 lines for a candidate title
    for line in lines[:10]:
        clean_line = line.strip()
        if clean_line and not is_junk(clean_line):
            # Clean up weird symbols sometimes found in PDFs
            return clean_line.replace('', '').strip()
    return "Section"

def index_pdfs():
    print("--- ADVANCED INDEXER STARTED ---")
    if not os.path.exists(MATERIALS_FOLDER): return

    files = [f for f in os.listdir(MATERIALS_FOLDER) if f.lower().endswith('.pdf')]
    files.sort()
    master_index = {}

    for filename in files:
        print(f"📖 Indexing: {filename}...")
        file_path = os.path.join(MATERIALS_FOLDER, filename)
        try:
            reader = PdfReader(file_path)
            pages_map = []
            for i, page in enumerate(reader.pages):
                text = page.extract_text()
                if text:
                    header = extract_header(text)
                    # Logic: Only add if different from previous and not junk
                    if not pages_map or pages_map[-1]['title'] != header:
                         pages_map.append({"page": i + 1, "title": header})
            master_index[filename] = pages_map
        except:
            print(f"⚠️ Could not read {filename}")

    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(master_index, f)
    print("✅ Index Updated.")

if __name__ == "__main__":
    index_pdfs()