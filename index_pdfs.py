import os
import json
from pypdf import PdfReader

MATERIALS_FOLDER = "materials"
OUTPUT_JSON = "pdf_data.json"

# STRINGS TO IGNORE (The Junk Filter)
IGNORE_LIST = ["telegram", "t.me", "www.", "http", "copyright", "uworld", "reserved", "page"]

def is_junk(text):
    """Checks if a line contains unwanted keywords."""
    text_lower = text.lower()
    if len(text) < 4: return True # Ignore tiny scraps
    if text.isdigit(): return True # Ignore page numbers
    for keyword in IGNORE_LIST:
        if keyword in text_lower:
            return True
    return False

def extract_header(text):
    """Finds the first real title, skipping junk."""
    lines = text.split('\n')
    for line in lines[:8]: # Check top 8 lines
        clean_line = line.strip()
        if clean_line and not is_junk(clean_line):
            return clean_line
    return "Section"

def index_pdfs():
    print("--- SMART INDEXER (WITH JUNK FILTER) ---")
    
    if not os.path.exists(MATERIALS_FOLDER):
        print("Error: Materials folder not found.")
        return

    files = [f for f in os.listdir(MATERIALS_FOLDER) if f.lower().endswith('.pdf')]
    files.sort()
    
    master_index = {}

    for filename in files:
        print(f"📖 Scanning: {filename}...")
        file_path = os.path.join(MATERIALS_FOLDER, filename)
        
        try:
            reader = PdfReader(file_path)
            pages_map = []
            
            for i, page in enumerate(reader.pages):
                text = page.extract_text()
                if text:
                    header = extract_header(text)
                    # Only add if it's different from the previous page's header
                    if not pages_map or pages_map[-1]['title'] != header:
                         pages_map.append({"page": i + 1, "title": header})
            
            master_index[filename] = pages_map
            
        except Exception as e:
            print(f"❌ Skipped {filename}: {e}")

    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(master_index, f)
        
    print(f"✅ Clean Index Saved to {OUTPUT_JSON}")

if __name__ == "__main__":
    index_pdfs()