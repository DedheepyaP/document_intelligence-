import sys
import os

# Add parent directory to path to import app modules
sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))

from app.core.config import settings
import shutil

def clear_chroma():
    persist_dir = settings.CHROMA_PERSIST_DIR
    
    print(f"🧹 Clearing ChromaDB at: {persist_dir}")
    
    if os.path.exists(persist_dir):
        try:
            shutil.rmtree(persist_dir)
            print(f"✅ Successfully removed {persist_dir}")
        except Exception as e:
            print(f"Error removing directory: {e}")
    else:
        print(f"ℹ️ Directory {persist_dir} does not exist. Nothing to clear.")

if __name__ == "__main__":
    clear_chroma()
