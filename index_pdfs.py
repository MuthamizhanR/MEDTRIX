import os
import json
from pypdf import PdfReader
import re

MATERIALS_FOLDER = "materials"
OUTPUT_JSON = "pdf_data.json"

def extract_header(text):
    """Attempts to find a meaningful title from the page text."""
    lines = text.split('\n')
    # Grab the first non-empty line that looks like a title
    for line in lines[:5]: # Check top 5 lines
        clean_line = line.strip()
        # Ignore page numbers or very short junk
        if len(clean_line) > 4 and not clean_line.isdigit():
            return clean_line
    return "Page"

def index_pdfs():
    print("--- PDF INDEXER STARTED ---")
    
    if not os.path.exists(MATERIALS_FOLDER):
        print("Error: Materials folder not found.")
        return

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
                # Extract text
                text = page.extract_text()
                if text:
                    header = extract_header(text)
                    # Clean up common UWorld headers if needed
                    header = header.replace("Medicine Full Course", "").strip()
                    
                    # If the header is new (different from previous page), add it to index
                    # This prevents 10 entries saying "Renal System" in a row
                    if not pages_map or pages_map[-1]['title'] != header:
                         pages_map.append({"page": i + 1, "title": header})
            
            master_index[filename] = pages_map
            
        except Exception as e:
            print(f"❌ Error reading {filename}: {e}")

    # Save to JSON file for the website to use
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(master_index, f)
        
    print("-" * 30)
    print(f"✅ Indexing Complete! Saved to {OUTPUT_JSON}")

if __name__ == "__main__":
    index_pdfs()