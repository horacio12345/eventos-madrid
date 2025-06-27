#!/usr/bin/env python3
"""
Punto de entrada principal para la aplicación FastAPI.
"""
import os
import sys

# Añadir el directorio raíz al PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Importar y ejecutar la aplicación
from backend.api.main import app

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("backend.api.main:app", host="0.0.0.0", port=8000, reload=True)
