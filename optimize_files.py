import os
import re
import html
import glob

def optimize_html_files():
    print("Starting optimization script...")
    files = glob.glob("*.html")
    
    if not files:
        print("ERROR: No .html files found in this folder.")
        print("Current folder is: " + os.getcwd())
        return

    print(f"Found {len(files)} files.")

    for file_path in files:
        print(f"Processing: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        # Create Backup
        if not os.path.exists(file_path + ".bak"):
            with open(file_path + ".bak", 'w', encoding='utf-8') as f:
                f.write(original_content)

        content = original_content

        # 1. CONTAINER LISTENERS
        container_script = """
    <script>
        window.addEventListener('message', function(e) {
            if(e.data.type === 'QUIZ_STATS') {
                e.data.subject = document.title;
                if (window.parent !== window) window.parent.postMessage(e.data, '*');
            }
        });
        window.addEventListener('message', function(event) {
            if (event.data === 'REQUEST_RANDOM_QUESTION') {
                try {
                    const iframes = document.querySelectorAll('.iframe-container iframe');
                    if (iframes.length > 0) {
                        const randomIframe = iframes[Math.floor(Math.random() * iframes.length)];
                        const srcdoc = randomIframe.getAttribute('srcdoc');
                        const match = srcdoc.match(/let questions = (\[.*?\]);/s);
                        if (match && match[1]) {
                            const txt = document.createElement("textarea");
                            txt.innerHTML = match[1];
                            const questions = JSON.parse(txt.value);
                            const randomQ = questions[Math.floor(Math.random() * questions.length)];
                            event.source.postMessage({ 
                                type: 'RANDOM_QUESTION_DATA', 
                                sourceFile: document.title,
                                question: randomQ 
                            }, event.origin);
                        }
                    }
                } catch (e) { console.error('Error extracting QOTD:', e); }
            }
        });
    </script>
    """
        if "</body>" in content and "REQUEST_RANDOM_QUESTION" not in content:
            content = content.replace("</body>", container_script + "\n</body>")

        # Mobile CSS for Container
        main_mobile_css = """
    <style>
        /* Mobile Optimization for Main Nav */
        @media (max-width: 768px) {
            .nav-buttons { display: flex; flex-wrap: wrap; gap: 8px; justify-content: center; }
            .nav-buttons button { flex: 1 1 45%; margin: 0; padding: 12px; font-size: 14px; }
            body { padding: 10px; }
            h1 { font-size: 1.5rem; text-align: center; }
        }
    </style>
    """
        if "</head>" in content and "/* Mobile Optimization for Main Nav */" not in content:
            content = content.replace("</head>", main_mobile_css + "\n</head>")

        # 2. INNER QUIZ MODIFICATIONS
        def process_iframe_match(match):
            full_tag = match.group(0)
            srcdoc_content = match.group(1)
            try:
                inner_code = html.unescape(srcdoc_content)
            except:
                return full_tag 
            
            inner_code = inner_code.replace("@dams_new_robot", "")

            analytics_js = """
        function sendAnalyticsToContainer() {
            try {
                const currentAnswers = (typeof answers !== 'undefined') ? answers : [];
                const currentQuestions = (typeof questions !== 'undefined') ? questions : [];
                const attemptedCount = currentAnswers.filter(a => a !== null).length;
                const totalQs = currentQuestions.length;
                const strikeRate = totalQs > 0 ? ((attemptedCount / totalQs) * 100).toFixed(2) : 0;
                const stats = {
                    type: 'QUIZ_STATS',
                    questionsAttempted: attemptedCount,
                    totalQuestions: totalQs,
                    strikeRate: strikeRate,
                    timeLeft: typeof timeRemaining !== 'undefined' ? timeRemaining : 0,
                    timestamp: new Date().toISOString()
                };
                window.parent.postMessage(stats, '*');
            } catch(e) { console.error('Analytics Error:', e); }
        }
            """
            if "function initQuiz()" in inner_code and "sendAnalyticsToContainer" not in inner_code:
                inner_code = inner_code.replace("function initQuiz()", analytics_js + "\n        function initQuiz()")

            if 'debugLog("Test submitted successfully");' in inner_code and "sendAnalyticsToContainer();" not in inner_code:
                inner_code = inner_code.replace(
                    'debugLog("Test submitted successfully");', 
                    'sendAnalyticsToContainer();\n                debugLog("Test submitted successfully");'
                )

            inner_mobile_css = """
            <style>
                /* Mobile Optimization for Quiz Iframe */
                @media (max-width: 640px) {
                    body { padding: 10px; }
                    .header-text { font-size: 1.25rem !important; }
                    .subheader-text { font-size: 0.8rem !important; }
                    .option-btn { padding: 12px; font-size: 15px; }
                    #question-text { font-size: 16px; }
                    .nav-panel { width: 85% !important; }
                    .flex-row { flex-direction: column; gap: 10px; }
                    #previous-btn, #next-btn, #mark-review, #nav-toggle, #submit-test { width: 100%; margin-bottom: 5px;}
                }
            </style>
            """
            if "</head>" in inner_code and "/* Mobile Optimization for Quiz Iframe */" not in inner_code:
                inner_code = inner_code.replace("</head>", inner_mobile_css + "\n</head>")

            new_srcdoc = html.escape(inner_code, quote=True)
            return f'<iframe srcdoc="{new_srcdoc}"'

        content = re.sub(r'<iframe srcdoc="(.*?)"', process_iframe_match, content, flags=re.DOTALL)

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"Done: {file_path}")

    print("\nAll files optimized successfully.")
    cleanup = input("Do you want to delete the backup (.bak) files now? (y/n): ").lower()
    if cleanup == 'y':
        bak_files = glob.glob("*.bak")
        for bf in bak_files:
            try: os.remove(bf)
            except: pass
        print("Cleanup finished!")
    else:
        print("Backups kept.")

if __name__ == "__main__":
    optimize_html_files()