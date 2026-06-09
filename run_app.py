"""Launcher for the Streamlit app.

Why this exists (Python 3.14 + Streamlit + ChromaDB import crash):
`import chromadb` eagerly imports OpenTelemetry, whose logging module builds a
Resource via a ThreadPoolExecutor *at import time*. On Python 3.14 that first
import fails when it happens inside Streamlit's script thread, with:
    RuntimeError: cannot schedule new futures after interpreter shutdown
(`streamlit run src/app.py` runs the script body on that thread, so the crash
hits there; it does not happen on the main thread.)

This launcher imports the heavy libraries here on the MAIN thread first. Module
code runs only once per process, so by the time Streamlit's script thread does
`import chromadb` it is a cached no-op and never re-runs the bad path.

Run the app with:
    .venv\\Scripts\\python.exe run_app.py
"""

import sys
from pathlib import Path

# --- Pre-import heavy deps on the main thread (they initialize cleanly here) ---
import chromadb  # noqa: F401  (pulls in the OpenTelemetry import that crashes on the script thread)
import sentence_transformers  # noqa: F401  (pre-warm the embedding stack too)

from streamlit.web import cli as stcli  # noqa: E402

if __name__ == "__main__":
    app_path = Path(__file__).resolve().parent / "src" / "app.py"
    sys.argv = ["streamlit", "run", str(app_path)]
    sys.exit(stcli.main())
