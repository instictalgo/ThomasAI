import sys
print(f"Python version: {sys.version}")
print(f"Python path: {sys.executable}")
print("Importing FastAPI...")
import fastapi
print(f"FastAPI version: {fastapi.__version__}")
print("Starting API server...")
import uvicorn
from api.main import app
print("API app imported successfully")
uvicorn.run(app, host="0.0.0.0", port=8000, log_level="debug")
