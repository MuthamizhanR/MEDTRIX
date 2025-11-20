import os
import mammoth
from xhtml2pdf import pisa
import io

# --- CONFIGURATION ---
SOURCE_FOLDER = "materials"
# ---------------------

def convert_to_pdf(docx_path, safe_mode=False):
    filename = os.path.basename(docx_path)
    pdf_filename = os.path.splitext(filename)[0] + ".pdf"
    pdf_path = os.path.join(SOURCE_FOLDER, pdf_filename)
    
    # CSS Styling
    css = """
    <style>
        @page { size: A4; margin: 2cm; }
        body { font-family: Helvetica, sans-serif; font-size: 12pt; line-height: 1.5; }
        h1, h2, h3 { color: #0056b3; margin-top: 20px; }
        p { margin-bottom: 10px; text-align: justify; }
        table { border-collapse: collapse; width: 100%; margin-bottom: 15px; }
        th { background-color: #00a8cc; color: white; padding: 8px; border: 1px solid #ddd; }
        td { padding: 8px; border: 1px solid #ddd; }
        img { max-width: 100%; height: auto; margin: 10px 0; }
        .alert { color: red; font-weight: bold; border: 1px solid red; padding: 10px; }
    </style>
    """

    try:
        with open(docx_path, "rb") as docx_file:
            if safe_mode:
                # Safe Mode: Convert strictly to text first, ignoring complex images/tables
                print(f"⚠️  Retrying {filename} in Safe Mode (Text Only)...")
                result = mammoth.convert_to_html(docx_file, ignore_empty_paragraphs=True)
            else:
                # Normal Mode
                result = mammoth.convert_to_html(docx_file)
                
            html_content = result.value

        # Add a warning if generated in Safe Mode
        if safe_mode:
            html_content = f"<div class='alert'>Note: This document was converted in Safe Mode. Some images may be missing.</div>" + html_content

        full_html = f"<html><head>{css}</head><body>{html_content}</body></html>"

        # Generate PDF
        with open(pdf_path, "wb") as pdf_file:
            pisa_status = pisa.CreatePDF(full_html, dest=pdf_file)

        if pisa_status.err:
            print(f"❌ Error creating PDF for {filename}")
            return False
        else:
            print(f"✅ Created: {pdf_filename}")
            return True

    except Exception as e:
        if not safe_mode:
            # If normal mode fails, try safe mode recursively
            return convert_to_pdf(docx_path, safe_mode=True)
        else:
            print(f"❌ FAILED {filename}: {str(e)}")
            return False

def main():
    if not os.path.exists(SOURCE_FOLDER):
        print(f"Error: Folder '{SOURCE_FOLDER}' not found.")
        return

    files = [f for f in os.listdir(SOURCE_FOLDER) if f.lower().endswith('.docx')]
    
    if not files:
        print("No .docx files found.")
        return

    print(f"Found {len(files)} documents. Processing...")
    
    success_count = 0
    for f in files:
        if convert_to_pdf(os.path.join(SOURCE_FOLDER, f)):
            success_count += 1
        
    print("-" * 30)
    print(f"Completed: {success_count}/{len(files)} converted.")

if __name__ == "__main__":
    main()