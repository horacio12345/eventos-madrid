.PHONY: install run-backend run-frontend format

# Instalar dependencias
install:
	pip install -r requirements.txt

# Iniciar backend
run-backend:
	cd backend && uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# Iniciar frontend (si usas Node.js)
run-frontend:
	cd frontend && npm run dev

# Formatear código Python
format:
	black .
	isort .
