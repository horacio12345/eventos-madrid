# 🎭 Frontend - Eventos Mayores Madrid

Frontend moderno construido con Next.js 14, TypeScript y Tailwind CSS para la plataforma de eventos para mayores en Madrid.

## 🚀 Instalación y Configuración

### Prerequisitos

- **Node.js 18+** (recomendado: v22.14.0 o superior)
- **npm** o **yarn**
- **Backend ejecutándose** en `http://localhost:8000`

### 1. Instalación de dependencias

```bash
cd frontend
npm install
```

### 2. Configuración de variables de entorno

El frontend usa estas variables de entorno (ya configuradas por defecto):

```bash
# Variables públicas de Next.js
NEXT_PUBLIC_API_URL=http://localhost:8000/api
NEXT_PUBLIC_APP_NAME="Eventos Mayores Madrid"
NODE_ENV=development
```

### 3. Ejecutar en desarrollo

```bash
npm run dev
```

La aplicación estará disponible en: **http://localhost:3000**

### 4. Build para producción

```bash
npm run build
npm start
```

## 📁 Estructura del Frontend

```
frontend/
├── app/                      # App Router de Next.js 14
│   ├── layout.tsx           # Layout principal
│   ├── page.tsx             # Página de inicio (eventos públicos)
│   ├── globals.css          # Estilos globales
│   └── admin/               # Panel de administración
│       ├── layout.tsx       # Layout del admin
│       ├── login/
│       ├── dashboard/
│       ├── fuentes/
│       └── logs/
├── components/              # Componentes React reutilizables
│   ├── EventCard.tsx        # Tarjeta de evento
│   ├── LoadingSpinner.tsx   # Spinner de carga
│   ├── Alert.tsx           # Componente de alertas
│   └── Modal.tsx           # Modal reutilizable
├── lib/                    # Utilidades y configuración
│   ├── api.ts              # Cliente API para backend
│   ├── types.ts            # Tipos TypeScript
│   └── utils.ts            # Funciones helper
├── public/                 # Assets estáticos
├── next.config.js          # Configuración Next.js
├── tailwind.config.js      # Configuración Tailwind
├── tsconfig.json           # Configuración TypeScript
└── package.json           # Dependencias y scripts
```

## 🎨 Características del Frontend

### 👥 **Vista Pública (Eventos)**
- **Página principal accesible** diseñada específicamente para personas mayores
- **Texto grande y legible** con alto contraste
- **Navegación simple** sin filtros complejos
- **Tarjetas de eventos** con información clara y completa
- **Categorías visuales** con emojis y colores
- **Responsive design** optimizado para móvil, tablet y desktop
- **Sin necesidad de registro** - acceso inmediato

### 🔐 **Panel de Administración**
- **Autenticación JWT** segura
- **Dashboard completo** con estadísticas en tiempo real
- **Gestión de fuentes web** (crear, editar, activar/desactivar, eliminar)
- **Sistema de testing** para probar fuentes antes de activarlas
- **Visualización de logs** del sistema con filtros
- **Trigger manual** de scraping
- **Interfaz moderna** y fácil de usar

### ⚡ **Características Técnicas**
- **Next.js 14** con App Router
- **TypeScript** para type safety
- **Tailwind CSS** para estilos responsive
- **Componentes modulares** y reutilizables
- **Estado compartido** con hooks personalizados
- **API client** con interceptors automáticos
- **Error handling** robusto
- **Loading states** en toda la aplicación

## 🔧 Scripts Disponibles

```bash
# Desarrollo
npm run dev                 # Servidor de desarrollo con hot reload

# Producción
npm run build              # Build optimizado para producción
npm start                  # Servidor de producción

# Calidad de código
npm run lint               # Linting con ESLint
npm run type-check         # Verificación de tipos TypeScript
```

## 📱 Diseño Responsive

### **Breakpoints Tailwind:**
- `xs`: 475px+ (móviles pequeños)
- `sm`: 640px+ (móviles)
- `md`: 768px+ (tablets)
- `lg`: 1024px+ (laptops)
- `xl`: 1280px+ (desktops)
- `2xl`: 1536px+ (pantallas grandes)

### **Optimizaciones para Mayores:**
- **Font size base**: 16px (móvil) → 18px (desktop)
- **Line height**: 1.6 para mejor legibilidad
- **Botones**: Mínimo 44px de altura (touch target)
- **Colores**: Alto contraste para mejor visibilidad
- **Espaciado**: Generoso para fácil navegación

## 🎯 Rutas de la Aplicación

### **Rutas Públicas:**
- `/` - Página principal con eventos
- `/admin/login` - Login del administrador

### **Rutas Admin (requieren autenticación):**
- `/admin/dashboard` - Dashboard principal
- `/admin/fuentes` - Gestión de fuentes web
- `/admin/logs` - Logs del sistema
- `/admin/config` - Configuración (futuro)

## 🔌 Integración con Backend

### **API Endpoints usados:**
```typescript
// Públicos
GET /api/eventos              # Lista de eventos
GET /api/eventos/{id}         # Detalle de evento
GET /api/categorias           # Categorías con conteo
GET /api/health              # Health check

// Admin (requieren JWT)
POST /api/admin/login         # Autenticación
GET /api/admin/fuentes        # Lista fuentes
POST /api/admin/fuentes       # Crear fuente
PUT /api/admin/fuentes/{id}   # Actualizar fuente
DELETE /api/admin/fuentes/{id} # Eliminar fuente
POST /api/admin/test-source   # Testear fuente
POST /api/admin/trigger-update # Trigger scraping
GET /api/admin/logs          # Logs sistema
```

### **Autenticación:**
- Token JWT almacenado en `localStorage`
- Interceptor automático en requests
- Redirección automática si token expira
- Logout manual disponible

## 🚀 Deployment

### **Con Docker (Recomendado):**
```bash
# Build imagen
docker build -t eventos-frontend .

# Ejecutar contenedor
docker run -p 3000:3000 -e NEXT_PUBLIC_API_URL=http://backend:8000/api eventos-frontend
```

### **Con Docker Compose:**
```yaml
# Ya incluido en docker-compose.yml del proyecto
services:
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://backend:8000/api
```

### **Build Manual:**
```bash
npm run build
npm start
```

## 🐛 Debugging y Desarrollo

### **Herramientas de desarrollo:**
- **React Developer Tools** - Extensión de navegador
- **Next.js DevTools** - Incluido en dev mode
- **Tailwind CSS IntelliSense** - VSCode extension
- **TypeScript** - Type checking en tiempo real

### **Logging:**
- Console logs automáticamente removidos en producción
- Error tracking con detalles específicos
- Network requests visibles en dev tools

### **Hot Reload:**
- Cambios en archivos `.tsx` se reflejan inmediatamente
- Cambios en Tailwind CSS se aplican al instante
- TypeScript errors se muestran en tiempo real

## 🔒 Seguridad

### **Implementado:**
- Headers de seguridad en `next.config.js`
- Validación de inputs en formularios
- Sanitización de datos de API
- JWT token expiration handling
- HTTPS ready (configurar en nginx)

### **CORS:**
- Backend configurado para permitir frontend
- Headers de origen verificados
- Requests preflight manejados

## 🎨 Customización

### **Colores y temas:**
```javascript
// tailwind.config.js
theme: {
  extend: {
    colors: {
      primary: { /* Azul principal */ },
      secondary: { /* Rosa secundario */ },
      // ... más colores
    }
  }
}
```

### **Tipografía:**
```css
/* globals.css */
:root {
  --font-inter: 'Inter', system-ui, sans-serif;
}
```

## 📞 Soporte

Para problemas específicos del frontend:

1. **Verificar logs del navegador** (F12 → Console)
2. **Comprobar network requests** (F12 → Network)
3. **Verificar que backend esté corriendo** en puerto 8000
4. **Limpiar cache del navegador** si hay problemas con assets

---

**🎭 Frontend desarrollado con ❤️ para conectar a nuestros mayores con la cultura madrileña**