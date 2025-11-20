import os
import mammoth
from xhtml2pdf import pisa
import re

SOURCE_FOLDER = "materials"

def clean_html(html):
    # 1. Replace complex lists with simple paragraphs to prevent "sequence item" errors
    html = html.replace("<ul>", "<div>").replace("</ul>", "</div>")
    html = html.replace("<ol>", "<div>").replace("</ol>", "</div>")
    html = html.replace("<li>", "<p>&bull; ").replace("</li>", "</p>")
    
    # 2. Remove images causing 'NoneType' errors
    # (We replace them with a placeholder text)
    html = re.sub(r'<img[^>]*>', ' [IMAGE REMOVED FOR PDF COMPATIBILITY] ', html)
    
    # 3. Simplify Tables (Prevent "Too Large" error)
    # We keep the data but remove the complex table structure if it's too nested
    # For now, we will try to just shrink the font in CSS, but if that fails, 
    # this regex removes height attributes that confuse the PDF engine.
    html = re.sub(r'height="[^"]+"', '', html)
    
    return html

def force_pdf(docx_path):
    filename = os.path.basename(docx_path)
    pdf_filename = os.path.splitext(filename)[0] + ".pdf"
    pdf_path = os.path.join(SOURCE_FOLDER, pdf_filename)
    
    if os.path.exists(pdf_path):
        print(f"⏭️  Skipping {filename} (PDF already exists)")
        return

    print(f"🔨 Force Converting: {filename}...")

    css = """
    <style>
        @page { size: A4; margin: 1cm; }
        body { font-family: Helvetica, sans-serif; font-size: 10pt; }
        /* Shrink tables to fit */
        table { font-size: 8pt; width: 100%; border: 1px solid #ccc; }
        td { border: 1px solid #ccc; padding: 2px; word-wrap: break-word; }
        /* Handle overflow */
        div { width: 100%; }
    </style>
    """

    try:
        with open(docx_path, "rb") as docx_file:
            # Generate HTML
            result = mammoth.convert_to_html(docx_file)
            raw_html = result.value
            
            # SANITIZE THE HTML
            safe_html = clean_html(raw_html)
            
            full_html = f"<html><head>{css}</head><body>{safe_html}</body></html>"

        with open(pdf_path, "wb") as pdf_file:
            pisa_status = pisa.CreatePDF(full_html, dest=pdf_file)

        if pisa_status.err:
            print(f"❌ Still failed: {filename}")
        else:
            print(f"✅ Success: {pdf_filename}")

    except Exception as e:
        print(f"❌ Error: {str(e)}")

def main():
    files = [f for f in os.listdir(SOURCE_FOLDER) if f.lower().endswith('.docx')]
    for f in files:
        force_pdf(os.path.join(SOURCE_FOLDER, f))

if __name__ == "__main__":
    main()