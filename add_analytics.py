import os

TARGET_FILE = "resources.html"

# 1. THE DASHBOARD DESIGN (CSS)
ANALYTICS_CSS = """
        /* ANALYTICS MODAL */
        #statsModal {
            display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0,0,0,0.8); z-index: 2000; align-items: center; justify-content: center;
            backdrop-filter: blur(5px); animation: fadeIn 0.3s;
        }
        .stats-content {
            background: var(--card-bg); width: 90%; max-width: 500px; padding: 25px;
            border-radius: 20px; border: 1px solid var(--border); position: relative;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        }
        .stats-header { font-size: 1.5rem; font-weight: bold; margin-bottom: 20px; display: flex; align-items: center; gap: 10px; }
        .close-stats { 
            position: absolute; top: 20px; right: 20px; cursor: pointer; font-size: 1.2rem; 
            background: var(--bg); width: 30px; height: 30px; border-radius: 50%; 
            display: flex; align-items: center; justify-content: center; transition: 0.2s;
        }
        .close-stats:hover { background: #ff4444; color: white; }

        /* PROGRESS BARS */
        .stat-row { margin-bottom: 15px; }
        .stat-label { display: flex; justify-content: space-between; margin-bottom: 5px; font-size: 0.9rem; font-weight: 600; }
        .progress-track { height: 10px; background: var(--bg); border-radius: 5px; overflow: hidden; }
        .progress-fill { height: 100%; background: var(--accent); border-radius: 5px; transition: width 1s ease; }
        
        .total-score { 
            text-align: center; margin: 20px 0; padding: 15px; background: var(--bg); 
            border-radius: 15px; font-size: 1.2rem; font-weight: bold; color: var(--primary);
        }
"""

# 2. THE BUTTON (HTML)
STATS_BUTTON = """
    <div style="text-align: center; margin-bottom: 20px;">
        <button onclick="openStats()" style="
            background: linear-gradient(45deg, #ff9800, #ff5722); color: white; border: none;
            padding: 10px 20px; border-radius: 25px; font-weight: bold; cursor: pointer;
            box-shadow: 0 4px 10px rgba(255, 87, 34, 0.3); transition: transform 0.2s;
        ">
            📊 View My Progress
        </button>
    </div>
"""

# 3. THE POPUP WINDOW (HTML)
MODAL_HTML = """
<div id="statsModal">
    <div class="stats-content">
        <div class="close-stats" onclick="closeStats()">✕</div>
        <div class="stats-header">📊 Study Report</div>
        
        <div class="total-score" id="totalProgress">Loading...</div>
        <div id="statsRows"></div>
        
        <div style="text-align:center; margin-top:20px; font-size:0.8rem; opacity:0.6">
            *Progress is saved on this device.
        </div>
    </div>
</div>
"""

# 4. THE MATH LOGIC (JS)
ANALYTICS_JS = """
    // ANALYTICS ENGINE
    function openStats() {
        document.getElementById('statsModal').style.display = 'flex';
        calculateStats();
    }

    function closeStats() {
        document.getElementById('statsModal').style.display = 'none';
    }

    function calculateStats() {
        const groups = document.querySelectorAll('.subject-group');
        let totalFiles = 0;
        let totalRead = 0;
        let html = '';

        groups.forEach(group => {
            const title = group.querySelector('.subject-title').innerText.split('(')[0];
            const cards = group.querySelectorAll('.resource-card');
            const count = cards.length;
            let read = 0;

            cards.forEach(card => {
                if(card.querySelector('.check-circle').classList.contains('checked')) {
                    read++;
                }
            });

            totalFiles += count;
            totalRead += read;
            const percent = Math.round((read / count) * 100);
            
            // Only show if there are files
            if(count > 0) {
                html += `
                <div class="stat-row">
                    <div class="stat-label">
                        <span>${title}</span>
                        <span>${read}/${count} (${percent}%)</span>
                    </div>
                    <div class="progress-track">
                        <div class="progress-fill" style="width: ${percent}%"></div>
                    </div>
                </div>`;
            }
        });

        // Update UI
        document.getElementById('statsRows').innerHTML = html;
        const totalPercent = totalFiles > 0 ? Math.round((totalRead / totalFiles) * 100) : 0;
        document.getElementById('totalProgress').innerHTML = `Total Completion: ${totalPercent}%`;
    }

    // Close modal on outside click
    document.getElementById('statsModal').addEventListener('click', function(e) {
        if (e.target === this) closeStats();
    });
"""

def inject_analytics():
    print("--- INJECTING ANALYTICS DASHBOARD ---")
    
    if not os.path.exists(TARGET_FILE):
        print(f"❌ Error: {TARGET_FILE} not found.")
        return

    with open(TARGET_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Inject CSS
    if "/* ANALYTICS MODAL */" not in content:
        content = content.replace("</style>", ANALYTICS_CSS + "\n    </style>")
        print("✅ CSS Added")
    
    # 2. Inject Button (Above the main container)
    if "View My Progress" not in content:
        content = content.replace('<div class="main-container">', STATS_BUTTON + '\n<div class="main-container">')
        print("✅ Button Added")

    # 3. Inject Modal HTML (At end of body)
    if 'id="statsModal"' not in content:
        content = content.replace("</body>", MODAL_HTML + "\n</body>")
        print("✅ Modal HTML Added")

    # 4. Inject JS Logic
    if "// ANALYTICS ENGINE" not in content:
        content = content.replace("</script>", ANALYTICS_JS + "\n</script>")
        print("✅ Logic Added")

    with open(TARGET_FILE, "w", encoding="utf-8") as f:
        f.write(content)

    print("-" * 30)
    print("🎉 Analytics successfully installed!")

if __name__ == "__main__":
    inject_analytics()