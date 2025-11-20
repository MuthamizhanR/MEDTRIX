import os

# --- CONFIGURATION ---
SOURCE_FOLDER = "materials"
# ---------------------

def clean_docx_files():
    if not os.path.exists(SOURCE_FOLDER):
        print(f"Error: Folder '{SOURCE_FOLDER}' not found.")
        return

    print(f"🧹 Scanning '{SOURCE_FOLDER}' for .docx files to delete...")
    
    files = [f for f in os.listdir(SOURCE_FOLDER) if f.lower().endswith('.docx')]
    
    if not files:
        print("✅ No .docx files found. Your folder is already clean!")
        return

    print(f"Found {len(files)} Word documents.")
    confirm = input("Type 'DELETE' to confirm you want to remove them: ")
    
    if confirm != "DELETE":
        print("❌ Operation cancelled. No files were touched.")
        return

    deleted_count = 0
    for f in files:
        file_path = os.path.join(SOURCE_FOLDER, f)
        try:
            os.remove(file_path)
            print(f"🗑️  Deleted: {f}")
            deleted_count += 1
        except Exception as e:
            print(f"❌ Error deleting {f}: {e}")

    print("-" * 30)
    print(f"✨ Cleanup complete! Removed {deleted_count} files.")

if __name__ == "__main__":
    clean_docx_files()