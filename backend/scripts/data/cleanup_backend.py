import os
import glob

def cleanup_files():
    files_to_delete = [
        "analyze_duplicates.py",
        "apply_library_updates.py",
        "audit_internal.py",
        "audit_result.txt",
        "audit_samples.py",
        "backup_missing_books.py",
        "check_duplicates.csv",
        "check_duplicates_cleaned.csv",
        "crawl_targeted_library.py",
        "crawl_update_childbook.py",
        "crawl_update_library.py",
        "crawler.py",  # Old crawler for library_items
        "export_duplicates.py",
        "fix_duplicates.py",
        "library_items_failed.csv",
        "library_items_updates.csv",
        "library_api.py", # Check if this is used?
        "verify_columns.py",
        "verify_cross_reference.py",
        "verify_library_source.py",
        "sample_missing.py",
        "childbook_direct_updates.csv",
        "targeted_library_updates.csv",
        "targeted_library_updates_final.csv"
    ]
    
    # Wildcard deletions
    wildcards = ["debug_*.py", "debug_*.html"]
    
    for w in wildcards:
        files_to_delete.extend(glob.glob(w))
        
    print(f"Cleaning up {len(files_to_delete)} files...")
    
    for fname in files_to_delete:
        if os.path.exists(fname):
            try:
                os.remove(fname)
                print(f"Deleted: {fname}")
            except Exception as e:
                print(f"Error deleting {fname}: {e}")
        else:
            # print(f"Skipped (not found): {fname}")
            pass
            
    print("Cleanup complete.")

if __name__ == "__main__":
    cleanup_files()
