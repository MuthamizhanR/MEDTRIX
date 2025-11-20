import os
import re
import glob

# HTML for the Search Bar (Styled with Tailwind)
SEARCH_BAR_HTML = """
  <div class="w-full max-w-lg mx-auto mb-6 sticky top-4 z-40">
    <div class="relative">
      <input type="text" id="testSearch" onkeyup="filterTests()" 
             placeholder="🔍 Search for a test..." 
             class="w-full px-5 py-4 text-lg rounded-full border-2 border-gray-200 focus:border-blue-500 focus:ring-4 focus:ring-blue-100 shadow-lg transition-all outline-none dark:bg-gray-800 dark:border-gray-700 dark:text-white dark:focus:ring-blue-900/50"
             autocomplete="off">
      <button onclick="document.getElementById('testSearch').value=''; filterTests()" 
              class="absolute right-4 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200">
        ✕
      </button>
    </div>
  </div>
"""

# JavaScript for Real-time Filtering
SEARCH_SCRIPT = """
<script>
    function filterTests() {
      var input, filter, container, buttons, button, txtValue, i;
      input = document.getElementById("testSearch");
      filter = input.value.toUpperCase();
      
      // Target the button grid specifically
      // We look for the container inside 'internal-index' that holds buttons
      container = document.getElementById("internal-index");
      buttons = container.getElementsByTagName("button");
      
      for (i = 0; i < buttons.length; i++) {
        button = buttons[i];
        // Skip the "Back" button if it happens to be inside (usually fixed positioned, but good to be safe)
        if (button.id === "back-to-index") continue;

        txtValue = button.textContent || button.innerText;
        if (txtValue.toUpperCase().indexOf(filter) > -1) {
          button.style.display = "";
        } else {
          button.style.display = "none";
        }
      }
    }
</script>
"""

def add_search_feature(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check if search bar already exists to avoid duplicates
    if 'id="testSearch"' in content:
        print(f"   ⏩ Skipping {file_path} (Search already added).")
        return

    print(f"   ✨ Adding search to: {file_path}")

    # 1. Insert Search Bar AFTER the main Header (<h1>...</h1>)
    # We look for the closing </h1> tag inside the internal-index div
    header_pattern = r'(<div id="internal-index"[^>]*>.*?<h1[^>]*>.*?</h1>)'
    
    # We use re.DOTALL so (.) matches newlines
    if re.search(header_pattern, content, flags=re.DOTALL):
        content = re.sub(header_pattern, r'\1' + SEARCH_BAR_HTML, content, count=1, flags=re.DOTALL)
    else:
        # Fallback: If H1 structure is complex, just put it at start of internal-index content
        content = content.replace('<div id="internal-index"', '<div id="internal-index"' + SEARCH_BAR_HTML)

    # 2. Insert JavaScript BEFORE the closing </body> tag
    content = content.replace('</body>', SEARCH_SCRIPT + '\n</body>')

    # 3. Save Changes
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

def process_all_files():
    html_files = glob.glob("*.html")
    # Filter out backup files
    html_files = [f for f in html_files if "_backup" not in f]
    
    if not html_files:
        print("❌ No HTML files found.")
        return

    print(f"🔍 Processing {len(html_files)} files...")
    print("-" * 40)

    for file_path in html_files:
        try:
            add_search_feature(file_path)
        except Exception as e:
            print(f"   ❌ Error in {file_path}: {e}")

    print("-" * 40)
    print("🎉 Search Bar added to all files!")

if __name__ == "__main__":
    process_all_files()