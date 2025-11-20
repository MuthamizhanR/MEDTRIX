import os
import re
import glob

def fix_single_file(file_path):
    print(f"Processing: {file_path}...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # --- SKIP IF ALREADY FIXED (Optional check to prevent double-patching) ---
    if "min-h-screen flex flex-col justify-center" in content and "bg-green-50" in content:
        print(f"   -> Skipping {file_path} (Already optimized).")
        return

    # ============================================================
    # STEP 1: FIX INDEX LAYOUT (Responsive Grid)
    # ============================================================
    # Remove old mobile CSS
    content = re.sub(r'@media \(max-width: 768px\) \{[^}]+\.nav-buttons[^}]+\}', '', content, flags=re.DOTALL)

    # Optimize Index Container (Center vertically)
    # Looks for <div id="internal-index" ... class="...">
    content = re.sub(
        r'(<div id="internal-index"[^>]*class=")([^"]*)(")', 
        r'\1\2 min-h-screen flex flex-col justify-center\3', 
        content
    )

    # Optimize Buttons (Make them chunky and grid-based)
    btn_container_pattern = r'(<div[^>]*max-w-xl space-y-4[^>]*>)'
    new_container_class = '<div class="grid grid-cols-1 md:grid-cols-2 gap-4 w-full max-w-4xl mx-auto p-4">'
    
    if re.search(btn_container_pattern, content):
        content = re.sub(btn_container_pattern, new_container_class, content)
        
    # Enlarge Button Styling
    btn_regex = r'(<button[^>]*onclick="showTest[^>]*class=")([^"]*)(")'
    new_btn_style = "w-full lift transition bg-white dark:bg-gray-800 text-gray-800 dark:text-gray-200 px-6 py-5 text-lg font-medium rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 my-2"
    content = re.sub(btn_regex, f'\\1{new_btn_style}\\3', content)

    # ============================================================
    # STEP 2: FIX IFRAME SCROLLING & HEIGHT
    # ============================================================
    # Remove fixed height="2000px"
    content = content.replace('height="2000px"', 'class="w-full min-h-screen" style="height: 100vh;"')
    
    # Allow body scrolling in srcdoc
    content = content.replace(
        '&lt;body class=&quot;bg-gray-100 font-sans transition-colors duration-300&quot;&gt;',
        '&lt;body class=&quot;bg-gray-100 font-sans transition-colors duration-300 min-h-screen overflow-y-auto&quot;&gt;'
    )

    # ============================================================
    # STEP 3: OPTIMIZE QUIZ LAYOUT (Mobile Full Screen)
    # ============================================================
    # Expand Card to Full Screen on Mobile
    card_regex = r'(class=&quot;)([^&]*bg-white rounded-lg shadow-md[^&]*)(&quot;)'
    
    def fix_card(match):
        old_class = match.group(2)
        new_class = old_class + " min-h-screen md:min-h-0 md:rounded-lg md:shadow-md rounded-none shadow-none flex flex-col justify-between"
        new_class = re.sub(r'p-\d+', 'p-5 md:p-8', new_class)
        return f'{match.group(1)}{new_class}{match.group(3)}'

    content = re.sub(card_regex, fix_card, content)

    # Increase Question Font Sizes
    qtext_regex = r'(id=&quot;question-text&quot; class=&quot;)([^&]*)(&quot;)'
    content = re.sub(qtext_regex, r'\1\2 text-lg md:text-xl leading-relaxed font-medium\3', content)

    # Increase Option Button Sizes
    opt_regex = r'(class=&quot;option-btn)([^&]*)(&quot;)'
    def enlarge_opt(match):
        cls = match.group(2)
        cls = re.sub(r'p-\d', 'p-4', cls)
        cls = cls + " text-base md:text-sm font-medium my-3"
        return f'{match.group(1)}{cls}{match.group(3)}'
    content = re.sub(opt_regex, enlarge_opt, content)

    # ============================================================
    # STEP 4: RESTORE & IMPROVE RESULT OPTIONS (High Contrast)
    # ============================================================
    search_anchor = "&lt;p&gt;&lt;strong&gt;Your Answer:&lt;/strong&gt;"

    # High Contrast Colors Logic
    options_logic = (
        "&lt;div class=&quot;my-4 space-y-3&quot;&gt;"
        "${q.options.map(opt =&gt; `"
        "&lt;div class=&quot;p-4 rounded-lg border text-base flex justify-between items-start ${"
        "opt.correct ? &quot;bg-green-100 border-green-600 text-green-900 dark:bg-green-900 dark:border-green-500 dark:text-green-50&quot; : "
        "(userAnswer === opt.label ? &quot;bg-red-100 border-red-600 text-red-900 dark:bg-red-900 dark:border-red-500 dark:text-red-50&quot; : "
        "&quot;bg-white border-gray-300 text-gray-900 dark:bg-gray-700 dark:border-gray-600 dark:text-gray-200&quot;)}&quot;&gt;"
        "&lt;div&gt;&lt;span class=&quot;font-bold mr-2&quot;&gt;${opt.label}.&lt;/span&gt; ${opt.text}&lt;/div&gt;"
        "&lt;div&gt;${opt.correct ? &quot;✅&quot; : (userAnswer === opt.label ? &quot;❌&quot; : &quot;&quot;)}&lt;/div&gt;"
        "&lt;/div&gt;`).join(&quot;&quot;)}"
        "&lt;/div&gt;"
    )

    # Clean previous injections if re-running
    clean_pattern = r'(&lt;div class=&quot;my-4.*?&quot;&gt;.*?&lt;/div&gt;)(\s*' + re.escape(search_anchor) + ')'
    content = re.sub(clean_pattern, r'\2', content)

    # Inject Logic
    content = content.replace(search_anchor, options_logic + search_anchor)

    # ============================================================
    # STEP 5: WRITE FILE
    # ============================================================
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"   ✅ Fixed.")

def process_all_html_files():
    # Find all .html files in the current directory
    html_files = glob.glob("*.html")
    
    # Exclude backup files if any exist
    html_files = [f for f in html_files if "_backup" not in f]
    
    if not html_files:
        print("❌ No HTML files found in this folder.")
        return

    print(f"🔍 Found {len(html_files)} HTML files. Starting batch fix...")
    print("-" * 40)

    count = 0
    for file_path in html_files:
        try:
            fix_single_file(file_path)
            count += 1
        except Exception as e:
            print(f"   ❌ Failed to process {file_path}: {e}")

    print("-" * 40)
    print(f"🎉 Batch Complete! Processed {count} files.")
    print("   You can now upload these to GitHub.")

if __name__ == "__main__":
    process_all_html_files()