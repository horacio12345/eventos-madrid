# 🗓️ Agenda Activa Madrid

**Plataforma web para descubrir planes y actividades en Madrid, seleccionados especialmente para personas mayores.**

![Agenda Activa](https://img.shields.io/badge/Status-Production%20Ready-green)
![Next.js](https://img.shields.io/badge/Next.js-14-black)
![FastAPI](https://img.shields.io/badge/FastAPI-Latest-009688)
![Docker](https://img.shields.io/badge/Docker-Ready-blue)

## 🎯 **Características Principales**

### 👥 **Para Usuarios** (Frontend Público)
- **📱 Diseño accesible** con texto grande y navegación simple
- **🔍 Búsqueda inteligente** de eventos por categoría y precio
- **📅 Organización temporal** (hoy, mañana, esta semana, próximamente)
- **💰 Filtros por precio** (eventos gratuitos, hasta 5€, 10€, 15€)
- **🎭 Categorías temáticas**: Cultura, Deporte y Salud, Formación, Cine, Paseos, Ocio
- **📱 100% responsive** optimizado para móvil, tablet y desktop

### 🔐 **Para Administradores** (Panel de Gestión)
- **🤖 Sistema de agentes** para procesar PDFs y extraer eventos automáticamente
- **📄 Procesamiento de documentos** con IA (OpenAI/Anthropic)
- **🔄 Detección de duplicados** automática con hashing de contenido
- **📊 Dashboard completo** con estadísticas en tiempo real
- **📁 Gestión de archivos** subidos con preview y eliminación
- **⚙️ Configuración flexible** de fuentes y frecuencias

## 🏗️ **Arquitectura Técnica**

### **Frontend** (Next.js 14 + TypeScript)
- **Framework**: Next.js 14 con App Router
- **Estilo**: Tailwind CSS con diseño system personalizado
- **Estado**: Hooks personalizados con SWR-like pattern
- **Componentes**: Modulares y reutilizables
- **API Client**: Axios con interceptors automáticos

### **Backend** (FastAPI + Python)
- **Framework**: FastAPI con SQLAlchemy 2.0
- **Base de datos**: SQLite (migrable a PostgreSQL)
- **IA**: LangChain + LangGraph para procesamiento de documentos
- **Scraping**: Playwright + BeautifulSoup
- **Extracción PDF**: Docling + PyMuPDF
- **Autenticación**: JWT tokens

### **Infraestructura**
- **Contenedores**: Docker + Docker Compose
- **Reverse Proxy**: Nginx con SSL automático
- **Deployment**: Optimizado para Hetzner Cloud
- **Storage**: Persistencia con volúmenes Docker

## 🚀 **Instalación y Desarrollo**

### **Prerequisitos**
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- API Key de OpenAI o Anthropic

### **Setup Rápido**
```bash
# 1. Clonar repositorio
git clone https://github.com/tu-usuario/agenda-activa-madrid.git
cd agenda-activa-madrid

# 2. Configuración automática
python scripts/setup.py

# 3. Configurar variables de entorno
cp .env.example .env
# Editar .env con tus API keys

# 4. Ejecutar en desarrollo
docker-compose up -d
```

### **Acceder a la aplicación**
- **Frontend público**: http://localhost:3000
- **Panel admin**: http://localhost:3000/admin
- **API docs**: http://localhost:8000/docs

## 📋 **Gestión del Sistema**

### **Scripts de Administración**
```bash
# Estado del sistema
python scripts/manage_system.py status

# Limpiar datos antiguos
python scripts/manage_system.py cleanup

# Testear agente específico
python scripts/test_scraping.py 1

# Inicializar base de datos
python scripts/init_db.py

# Insertar fuentes de ejemplo
python scripts/seed_sources.py
```

### **Gestión de Agentes**
1. **Crear agente** en el panel admin
2. **Subir PDF** con eventos
3. **Procesar documento** con IA
4. **Revisar eventos** extraídos
5. **Activar agente** para uso automático

## 🌐 **Deployment en Producción**

### **Hetzner Cloud** (Recomendado)
```bash
# Crear servidor
hcloud server create --name agenda-activa --type cx21 --image ubuntu-22.04

# Subir código
scp -r . root@SERVER_IP:/root/agenda-activa

# En el servidor
ssh root@SERVER_IP
cd /root/agenda-activa
docker-compose up -d --build

# Configurar SSL
certbot --nginx -d tu-dominio.com
```

### **Variables de Entorno Producción**
```env
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=clave_super_segura_32_caracteres
ADMIN_PASSWORD=password_muy_seguro
OPENAI_API_KEY=sk-tu_api_key_real
ALLOWED_ORIGINS=["https://tu-dominio.com"]
```

## 🛠️ **Configuración de Agentes**

### **Ejemplo: Procesar PDFs automáticamente**
```python
# El sistema puede procesar automáticamente PDFs como:
- Boletines municipales con eventos
- Programación de centros culturales
- Newsletters de asociaciones
- Calendarios de actividades

# Configuración en panel admin:
1. Nombre del agente
2. Frecuencia de procesamiento
3. Filtros por precio/categoría
4. Mapeo de campos específicos
```

## 📊 **Características del Sistema**

| Característica | Descripción |
|---------------|-------------|
| **Automatización** | Procesamiento automático de documentos con IA |
| **Deduplicación** | Eliminación automática de eventos duplicados |
| **Escalabilidad** | Arquitectura preparada para múltiples fuentes |
| **Accesibilidad** | Diseño optimizado para personas mayores |
| **Performance** | Caching inteligente y queries optimizadas |
| **Seguridad** | Autenticación JWT + headers de seguridad |

## 🎨 **Personalización**

### **Colores y Branding**
```css
/* En frontend/app/globals.css */
:root {
  --color-primary: #7033ff;
  --color-secondary: #edf0f4;
  --color-accent: #e2ebff;
}
```

### **Categorías de Eventos**
Editar `frontend/lib/utils.ts` para personalizar categorías:
```typescript
const CATEGORIAS = [
  { nombre: "Cultura", emoji: "🎭" },
  { nombre: "Deporte y Salud", emoji: "🏃" },
  // Añadir más...
];
```

## 🐛 **Troubleshooting**

### **Problemas Comunes**

| Problema | Solución |
|----------|----------|
| **Port 3000 ocupado** | `lsof -ti:3000 \| xargs kill -9` |
| **Error de permisos Docker** | `sudo usermod -aG docker $USER` |
| **API no responde** | `docker-compose logs backend` |
| **Build falla** | `docker-compose build --no-cache` |

### **Logs y Debugging**
```bash
# Ver logs en tiempo real
docker-compose logs -f

# Logs específicos
docker-compose logs backend
docker-compose logs frontend

# Estado de contenedores
docker-compose ps
```

## 📈 **Roadmap Futuro**

- [ ] **Integración con APIs públicas** (Ayuntamiento de Madrid)
- [ ] **Sistema de notificaciones** por email/SMS
- [ ] **App móvil** React Native
- [ ] **Geolocalización** para eventos cercanos
- [ ] **Sistema de favoritos** y recomendaciones
- [ ] **Multi-ciudad** (Barcelona, Valencia, etc.)

## 🤝 **Contribuir**

1. Fork del repositorio
2. Crear rama feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

## 📄 **Licencia**

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

## 🆘 **Soporte**

- **Documentación**: Ver carpetas `frontend/README.md` y `scripts/README.md`
- **Issues**: GitHub Issues
- **Email**: contacto@tu-dominio.com

---

**🎭 Desarrollado con ❤️ para conectar a nuestros mayores con la cultura madrileña**