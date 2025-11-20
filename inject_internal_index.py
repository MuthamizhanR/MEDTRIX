import os
import re
from glob import glob

INDEX_TEMPLATE = """
<!-- INTERNAL INDEX PAGE ADDED -->
<div id="internal-index" class="min-h-screen flex flex-col items-center justify-start p-6 bg-gray-100 dark:bg-gray-900">
  <h1 class="text-3xl font-bold text-gray-800 dark:text-white mt-10 mb-6">📘 Combined Test Index</h1>
  <div class="w-full max-w-xl space-y-4">
    {BUTTONS_HERE}
  </div>
</div>

<style>
  .lift:hover { transform: translateY(-3px); }
</style>
"""

# --- MODIFIED: Back button moved to top-left (top-4 left-4) ---
BACK_BUTTON = """
<button id="back-to-index"
  class="fixed top-4 left-4 z-50 bg-blue-600 text-white px-4 py-2 rounded-full shadow-lg hover:bg-blue-700 transition">
  ⬅ Back
</button>

<script>
document.getElementById("back-to-index").onclick = function() {
    document.getElementById("internal-index").style.display = "block";
    document.getElementById("tests-area").style.display = "none";
    window.scrollTo(0,0);
};
</script>
"""

SHOWTEST_PATCH = """
<script>
if (typeof showTest === 'function') {
    const originalShowTest = showTest;
    showTest = function(id) {
        document.getElementById("internal-index").style.display = "none";
        document.getElementById("tests-area").style.display = "block";
        originalShowTest(id);
    };
}
</script>
"""

WRAP_TESTS_AREA_START = '<div id="tests-area" style="display:none;">'
WRAP_TESTS_AREA_END = '</div>'

def extract_nav_buttons(html):
    block_match = re.search(r'(<div[^>]+class="[^"]*nav-buttons[^"]*"[\s\S]*?</div>)', html)
    if not block_match:
        return None, None
    
    block = block_match.group(1)
    buttons = []
    
    for btn in re.findall(r'<button[^>]*onclick="showTest\(\'(.*?)\'\)"[^>]*>(.*?)</button>', block, re.DOTALL):
        test_id = btn[0]
        label = re.sub(r'\s+', ' ', re.sub(r'<[^>]*>', '', btn[1])).strip()
        buttons.append((test_id, label))
    
    return block, buttons


def build_tailwind_buttons(buttons):
    out = ""
    for test_id, label in buttons:
        out += f"""
        <button onclick="showTest('{test_id}')"
          class="w-full lift transition bg-white dark:bg-gray-800 text-gray-800 dark:text-gray-200 px-5 py-4 rounded-xl shadow hover:shadow-xl">
          {label}
        </button>
        """
    return out


def process_file(path):
    with open(path, "r", encoding="utf-8") as f:
        html = f.read()

    nav_block, buttons = extract_nav_buttons(html)
    if not buttons:
        print(f"❌ No nav-buttons found in {path}")
        return
    
    print(f"✔ Processing {path} – {len(buttons)} buttons found.")

    # backup
    bak = path + ".bak"
    if not os.path.exists(bak):
        with open(bak, "w", encoding="utf-8") as bf:
            bf.write(html)

    # Remove nav block
    html = html.replace(nav_block, "")

    # Insert Tailwind index page
    button_html = build_tailwind_buttons(buttons)
    internal_index = INDEX_TEMPLATE.replace("{BUTTONS_HERE}", button_html)

    # Wrap all test containers
    html = re.sub(r'(</div>\s*</body>)', WRAP_TESTS_AREA_END + r"\1", html, 1)
    
    # Insert start of tests-area
    if WRAP_TESTS_AREA_START not in html:
        html = html.replace("<hr/>", "<hr/>\n" + WRAP_TESTS_AREA_START, 1)

    # Insert index at top of body
    if "<body>" in html:
        html = html.replace("<body>", "<body>\n" + internal_index, 1)

    # Add back button and showTest patch
    if "</body" in html:
        final_injection = BACK_BUTTON + SHOWTEST_PATCH + "\n"
        html = html.replace("</body>", final_injection + "</body>", 1)
        
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"   → ✔ Transformed successfully.\n")

# --- NEW FUNCTION: Deletes .bak files ---
def delete_backup_files():
    folder = os.getcwd()
    bak_files = glob(os.path.join(folder, "*.html.bak"))
    if not bak_files:
        print("ℹ No .bak files found to delete.")
        return

    print(f"\n🧹 Cleaning up {len(bak_files)} backup file(s)...")
    for bak_file in bak_files:
        try:
            os.remove(bak_file)
            print(f"   → Deleted: {os.path.basename(bak_file)}")
        except OSError as e:
            print(f"   → Error deleting {os.path.basename(bak_file)}: {e}")
    print("Cleanup complete.")

# MAIN
folder = os.getcwd()
files = glob(os.path.join(folder, "*.html"))

print(f"\n📂 Found {len(files)} HTML files.\n")

for f in files:
    if f.endswith(".bak"):
        continue
    process_file(f)

# --- NEW STEP: Check if cleanup should run ---
# The user wants a script to delete the files, so we make it optional 
# and prompt them to confirm before deleting them permanently.
confirm_deletion = input("\n✅ HTML transformation successful. Do you want to delete all .html.bak backup files now? (yes/no): ")

if confirm_deletion.lower() == 'yes':
    delete_backup_files()

print("\n🎉 ALL FILES PROCESSED!\n")
