from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent
FRONTEND_DIR = ROOT_DIR / "frontend" 
BACKEND_STATIC = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"