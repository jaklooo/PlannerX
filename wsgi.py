"""WSGI entry point for PlannerX."""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Ensure data directory exists
BASE_DIR = Path(__file__).parent
data_dir = BASE_DIR / "data"
data_dir.mkdir(exist_ok=True)

from app import create_app

# Create application instance
app = create_app(os.getenv("FLASK_ENV", "production"))

if __name__ == "__main__":
    # Enable URL map adapter to allow URLs without trailing slash
    app.url_map.strict_slashes = False
    app.run(host='localhost', port=5000, debug=True)
