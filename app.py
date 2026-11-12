"""Streamlit Community Cloud entry point. Run: streamlit run app.py."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from wisata_madura.web.app import main

if __name__ == "__main__":
    main()
