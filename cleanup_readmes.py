import os
import glob

def cleanup():
    print("Cleaning up rogue .README.md files...")
    files_to_delete = glob.glob("*.README.md")
    
    deleted_count = 0
    for f in files_to_delete:
        try:
            os.remove(f)
            print(f"✅ Deleted: {f}")
            deleted_count += 1
        except Exception as e:
            print(f"❌ Failed to delete {f}: {e}")
            
    print(f"\nDone! Successfully deleted {deleted_count} rogue files.")
    print("Your original README.md remains safe and untouched.")

if __name__ == "__main__":
    cleanup()
