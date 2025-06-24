# 🎭 Eventos Mayores Madrid

**Plataforma inteligente de agregación automática de eventos gratuitos y de bajo coste para personas mayores en la Comunidad de Madrid.**

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)
![Next.js](https://img.shields.io/badge/Next.js-14+-black.svg)
![LangGraph](https://img.shields.io/badge/LangGraph-0.4.8-purple.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## 🌟 Características Principales

- 🤖 **Scraping Inteligente**: Utiliza LangChain y LangGraph para extraer información de múltiples fuentes web
- 📄 **Procesamiento Avanzado**: Maneja HTML, PDFs complejos e imágenes con OCR
- 🎯 **Enfoque en Accesibilidad**: Interfaz ultra simple diseñada para personas mayores
- ⚡ **Actualización Automática**: Sistema de scheduler configurable para mantener eventos actualizados
- 🔧 **Panel de Administración**: Gestión completa de fuentes con sistema de testing
- 🐳 **Dockerizado**: Deployment sencillo con Docker Compose

## 🏗️ Arquitectura Técnica

### Backend
- **FastAPI** - API REST moderna y rápida
- **SQLite** - Base de datos ligera y eficiente
- **LangGraph** - Orquestación inteligente de scraping
- **Playwright** - Automation web para sitios con JavaScript
- **Docling** - Extracción avanzada de PDFs
- **APScheduler** - Programación de tareas automáticas

### Frontend
- **Next.js 14** - Framework React con SSR y App Router
- **TypeScript** - Tipado estático para mayor robustez
- **Tailwind CSS** - Estilos responsive y accesibles

## 🚀 Instalación Rápida

### Prerrequisitos
- Python 3.11+
- Node.js 18+
- Docker y Docker Compose (recomendado)

### 1. Clonar el Repositorio
```bash
git clone https://github.com/tu-usuario/eventos-mayores-madrid.git
cd eventos-mayores-madrid
```

### 2. Configuración de Entorno
```bash
# Copiar configuración de ejemplo
cp .env.example .env

# Editar variables de entorno
nano .env
```

### 3. Desarrollo con Docker (Recomendado)
```bash
# Iniciar servicios de desarrollo
docker-compose up -d backend frontend redis

# Ver logs
docker-compose logs -f backend
```

### 4. Desarrollo Local (Alternativo)

#### Backend
```bash
# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Instalar dependencias
pip install -r requirements.txt

# Instalar Playwright browsers
playwright install

# Inicializar base de datos
python scripts/init_db.py

# Cargar fuentes iniciales
python scripts/seed_sources.py

# Ejecutar servidor
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend
```bash
cd frontend

# Instalar dependencias
npm install

# Ejecutar en modo desarrollo
npm run dev
```

## 📊 URLs de Desarrollo

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **Documentación API**: http://localhost:8000/docs
- **Admin Panel**: http://localhost:3000/admin

## 🎯 Uso Básico

### Para Usuarios Finales
1. Visitar http://localhost:3000
2. Ver lista cronológica de eventos
3. Hacer clic en eventos para más detalles
4. ¡No requiere registro ni login!

### Para Administradores
1. Acceder a http://localhost:3000/admin
2. Login con credenciales configuradas en `.env`
3. Gestionar fuentes de datos
4. Probar nuevas fuentes antes de activarlas
5. Monitorear logs del sistema

## 🔧 Configuración de Fuentes

### Añadir Nueva Fuente Web
```python
# Ejemplo de configuración en el panel admin
{
    "nombre": "Ayuntamiento de Madrid",
    "url": "https://www.madrid.es/eventos",
    "tipo": "HTML",
    "configuracion": {
        "selectors": {
            "titulo": ".evento-titulo",
            "fecha": ".evento-fecha",
            "precio": ".evento-precio"
        },
        "filtros": {
            "max_precio": 15,
            "palabras_clave": ["mayores", "senior"]
        }
    },
    "frecuencia": "0 9 * * 1"  # Lunes 9:00 AM
}
```

## 🧪 Testing

```bash
# Tests backend
pytest backend/tests/

# Tests con coverage
pytest --cov=backend backend/tests/

# Tests específicos
pytest backend/tests/test_scraping/ -v

# Tests de integración
pytest backend/tests/ -m integration
```

## 📚 Documentación

- [Guía de Administración](docs/ADMIN_GUIDE.md)
- [API Documentation](docs/API.md)
- [Guía de Deployment](docs/DEPLOYMENT.md)
- [Contribuir al Proyecto](docs/CONTRIBUTING.md)

## 🔄 Comandos Útiles

### Desarrollo
```bash
# Formatear código
black backend/ && isort backend/

# Linting
ruff check backend/

# Type checking
mypy backend/

# Actualizar base de datos
alembic upgrade head

# Crear nueva migración
alembic revision --autogenerate -m "descripcion"
```

### Docker
```bash
# Rebuild completo
docker-compose build --no-cache

# Ver logs específicos
docker-compose logs -f backend

# Ejecutar comando en contenedor
docker-compose exec backend python scripts/test_scraping.py

# Limpiar volúmenes
docker-compose down -v
```

## 📋 Estructura del Proyecto

```
proyecto-eventos-mayores/
├── backend/           # API FastAPI
├── frontend/          # App Next.js
├── scripts/           # Scripts de utilidad
├── docs/             # Documentación
├── data/             # Base de datos y logs
└── docker-compose.yml
```

## 🤝 Contribuir

1. Fork el proyecto
2. Crear rama de feature (`git checkout -b feature/nueva-caracteristica`)
3. Commit cambios (`git commit -am 'Añadir nueva característica'`)
4. Push a la rama (`git push origin feature/nueva-caracteristica`)
5. Crear Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo [LICENSE](LICENSE) para detalles.

## 👥 Equipo

- **Desarrollo Backend**: LangChain + FastAPI + SQLAlchemy
- **Desarrollo Frontend**: Next.js + TypeScript + Tailwind
- **Scraping Inteligente**: LangGraph + Playwright + Docling
- **DevOps**: Docker + GitHub Actions

## 🔗 Enlaces Útiles

- [LangChain Documentation](https://python.langchain.com/)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)
- [Playwright Documentation](https://playwright.dev/python/)

## 📊 Roadmap

- [x] ✅ Setup inicial del proyecto
- [x] ✅ Motor de scraping básico
- [x] ✅ API REST completa
- [x] ✅ Frontend responsive
- [ ] 🔄 Panel admin avanzado
- [ ] 📱 PWA mobile
- [ ] 🤖 Chat IA para recomendaciones
- [ ] 📧 Sistema de notificaciones
- [ ] 📊 Analytics y métricas

---

**🎭 Eventos Mayores Madrid** - Conectando a nuestros mayores con la cultura y el ocio de la ciudad.