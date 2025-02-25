import os
import glob

def delete_webp_files(folder_path):
    """Deletes all .webp files in the specified folder."""
    webp_files = glob.glob(os.path.join(folder_path, "*.webp"))
    for file_path in webp_files:
        try:
            os.remove(file_path)
            print(f"Deleted: {file_path}")
        except OSError as e:
            print(f"Error deleting {file_path}: {e}")

# Example usage:
folder_path = "src/data/tiles"  # Replace with the actual path to your folder
delete_webp_files(folder_path)
print("All .webp files deleted from the specified folder.")