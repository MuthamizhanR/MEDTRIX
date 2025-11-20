import os

TARGET_FILE = "resources.html"

# 1. The CSS to Inject (Green Ticks & Layout)
NEW_CSS = """
        /* --- AUTO-INJECTED CHECKBOX STYLES --- */
        .check-circle {
            width: 24px; height: 24px; 
            border: 2px solid var(--accent); border-radius: 50%;
            margin-right: 15px; cursor: pointer; flex-shrink: 0;
            display: flex; align-items: center; justify-content: center;
            transition: 0.2s;
        }
        .check-circle.checked {
            background: #28a745; border-color: #28a745; color: white;
        }
        .check-circle.checked::after { content: '✓'; font-size: 14px; font-weight: bold; }
        
        /* Adjust card layout to fit checkbox */
        .resource-card { align-items: center; }
"""

# 2. The JavaScript to Inject (Save Progress logic)
NEW_JS = """
    /* --- AUTO-INJECTED READ MARKER LOGIC --- */
    function toggleRead(btn, id) {
        btn.classList.toggle('checked');
        if (btn.classList.contains('checked')) {
            localStorage.setItem('read_' + id, 'true');
        } else {
            localStorage.removeItem('read_' + id);
        }
    }

    // Restore state on load
    window.addEventListener('load', function() {
        const checks = document.querySelectorAll('.check-circle');
        checks.forEach(check => {
            const id = check.getAttribute('data-id');
            if (localStorage.getItem('read_' + id) === 'true') {
                check.classList.add('checked');
            }
        });
    });
"""

def upgrade_html():
    if not os.path.exists(TARGET_FILE):
        print(f"❌ Error: Could not find {TARGET_FILE}")
        return

    print(f"⚙️  Upgrading {TARGET_FILE}...")
    
    with open(TARGET_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    # SAFETY CHECK: Don't inject twice
    if "check-circle" in content:
        print("⚠️  It looks like the styles are already there! Aborting to prevent duplicates.")
        return

    # INJECT CSS (Before the closing </style> tag)
    if "</style>" in content:
        content = content.replace("</style>", NEW_CSS + "\n    </style>")
        print("✅ CSS Styles injected.")
    else:
        print("❌ Error: Could not find </style> tag.")
        return

    # INJECT JS (Before the closing </script> tag)
    # We look for the LAST script tag usually at the bottom
    if "</script>" in content:
        # We use rsplit to find the last occurrence to be safe, or just replace the tag
        content = content.replace("</script>", NEW_JS + "\n</script>")
        print("✅ JavaScript Logic injected.")
    else:
        print("❌ Error: Could not find </script> tag.")
        return

    # SAVE CHANGES
    with open(TARGET_FILE, "w", encoding="utf-8") as f:
        f.write(content)

    print("-" * 30)
    print("🚀 Upgrade Complete! Your site now supports 'Mark as Completed'.")

if __name__ == "__main__":
    upgrade_html()