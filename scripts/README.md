# 🛠️ Scripts de Gestión - Eventos Mayores Madrid

Esta carpeta contiene los scripts esenciales para la configuración, gestión y mantenimiento del sistema.

## 📋 Scripts Disponibles

### 🚀 `setup.py` - Configuración Inicial Completa
```bash
python scripts/setup.py
```
**Propósito**: Automatiza toda la configuración inicial del sistema desde cero.

**Lo que hace**:
- ✅ Verifica versión de Python (3.11+)
- ✅ Crea directorios necesarios (`data/`, `logs/`, etc.)
- ✅ Verifica dependencias críticas
- ✅ Instala browsers de Playwright
- ✅ Crea archivo `.env.example`
- ✅ Inicializa base de datos SQLite
- ✅ Inserta fuentes de ejemplo
- ✅ Crea configuración nginx básica

**Cuándo usar**: Primera vez que instalas el sistema.

---

### 🗄️ `init_db.py` - Inicializar Base de Datos
```bash
python scripts/init_db.py
```
**Propósito**: Crear tablas de base de datos y configuración inicial.

**Lo que hace**:
- Crea todas las tablas SQLAlchemy
- Inserta configuración por defecto del sistema
- Configura parámetros iniciales

**Cuándo usar**: 
- Primera instalación
- Después de cambios en modelos de base de datos
- Para resetear configuración

---

### 🌱 `seed_sources.py` - Fuentes de Ejemplo
```bash
python scripts/seed_sources.py
```
**Propósito**: Insertar fuentes web de ejemplo pre-configuradas.

**Fuentes incluidas**:
- 🏛️ Ayuntamiento de Madrid - Actividades Mayores
- 🎭 Comunidad de Madrid - Centros Culturales  
- 👴 IMSERSO - Actividades
- 📚 Bibliotecas Municipales Madrid

**Características**:
- Todas las fuentes están **INACTIVAS** por defecto
- Configuración completa de selectores CSS
- Filtros por precio y palabras clave
- Programación automática configurada

**Cuándo usar**:
- Primera instalación
- Para tener ejemplos de configuración
- Como base para crear nuevas fuentes

---

### 🧪 `test_scraping.py` - Testing de Scraping
```bash
# Ver fuentes disponibles
python scripts/test_scraping.py

# Testear fuente específica por ID
python scripts/test_scraping.py 1

# Testear fuente por nombre
python scripts/test_scraping.py --name "ayuntamiento"
```
**Propósito**: Probar configuraciones de scraping sin afectar la base de datos.

**Lo que hace**:
- 🎯 Testa extracción de una fuente específica
- 📊 Muestra estadísticas del test
- 👀 Preview de primeros 3 eventos encontrados
- 💾 Guarda resultado completo en JSON
- 🐛 Detecta errores de configuración

**Resultado del test**:
- Tiempo de ejecución
- Número de eventos encontrados
- Preview de eventos extraídos
- Errores detallados si los hay
- Archivo JSON con resultado completo

**Cuándo usar**:
- Antes de activar una fuente nueva
- Para debuggear problemas de extracción
- Para verificar cambios en selectores
- Para ajustar configuraciones

---

### 🛠️ `manage_system.py` - Gestión del Sistema
```bash
# Estado general del sistema
python scripts/manage_system.py status

# Limpiar datos antiguos (30 días por defecto)
python scripts/manage_system.py cleanup [días]

# Ejecutar scraping manual
python scripts/manage_system.py scraping [ID_fuente]

# Controlar scheduler
python scripts/manage_system.py scheduler start|stop|status|reload

# Listar fuentes
python scripts/manage_system.py sources

# Ayuda completa
python scripts/manage_system.py help
```
**Propósito**: Gestión completa y mantenimiento del sistema en producción.

#### Comandos detallados:

**📊 `status`**:
- Estadísticas de eventos y fuentes
- Últimos logs de scraping
- Estado del scheduler
- Próximas ejecuciones programadas

**🧹 `cleanup [días]`**:
- Elimina eventos inactivos antiguos
- Elimina logs antiguos
- Libera espacio en disco
- Por defecto: 30 días

**⚡ `scraping [ID]`**:
- Ejecuta scraping manual inmediato
- Sin ID: todas las fuentes activas
- Con ID: fuente específica
- Muestra resultado detallado

**⏰ `scheduler <acción>`**:
- `start`: Inicia programador automático
- `stop`: Detiene programador  
- `status`: Estado y próximas ejecuciones
- `reload`: Reinicia cargando nuevas configuraciones

**🌐 `sources`**:
- Lista todas las fuentes configuradas
- Estado (activa/inactiva)
- Último resultado de scraping
- Estadísticas de eventos

**Cuándo usar**:
- Monitoreo diario del sistema
- Mantenimiento programado
- Resolución de problemas
- Gestión de producción

---

## 🚀 Flujo de Trabajo Recomendado

### Primera Instalación:
```bash
1. python scripts/setup.py                    # Configuración completa
2. # Editar .env con tus configuraciones
3. python scripts/manage_system.py status     # Verificar sistema
4. python scripts/test_scraping.py            # Ver fuentes disponibles
```

### Añadir Nueva Fuente:
```bash
1. # Crear fuente en panel admin
2. python scripts/test_scraping.py ID         # Testear configuración
3. # Activar fuente en panel admin
4. python scripts/manage_system.py scheduler reload  # Recargar programación
```

### Mantenimiento Diario:
```bash
1. python scripts/manage_system.py status     # Estado del sistema
2. python scripts/manage_system.py cleanup    # Limpiar datos antiguos
```

### Resolución de Problemas:
```bash
1. python scripts/manage_system.py sources    # Ver estado de fuentes
2. python scripts/test_scraping.py ID         # Testear fuente problemática
3. python scripts/manage_system.py scheduler status  # Estado del programador
```

## 📝 Archivos Generados

### Logs y Resultados:
- `test_results_*.json` - Resultados de tests de scraping
- `data/database.db` - Base de datos SQLite
- `data/logs/` - Logs del sistema
- `logs/` - Logs de aplicación

### Configuración:
- `.env.example` - Plantilla de configuración
- `nginx/nginx.conf` - Configuración de nginx
- `data/` - Directorio de datos

## ⚠️ Notas Importantes

1. **Permisos**: Los scripts necesitan permisos de escritura en `data/` y `logs/`

2. **Dependencias**: Verifica que todas las dependencias estén instaladas antes de ejecutar

3. **Backup**: Haz backup de `data/database.db` antes de operaciones críticas

4. **Producción**: En producción, ejecuta `cleanup` regularmente para mantener rendimiento

5. **Testing**: Siempre testa fuentes con `test_scraping.py` antes de activarlas

## 🆘 Solución de Problemas

### Error de permisos:
```bash
chmod +x scripts/*.py
```

### Error de dependencias:
```bash
pip install -r requirements.txt
python -m playwright install chromium
```

### Error de base de datos:
```bash
python scripts/init_db.py
```

### Scheduler no funciona:
```bash
python scripts/manage_system.py scheduler stop
python scripts/manage_system.py scheduler start
```

---

**💡 Tip**: Todos los scripts tienen ayuda detallada con `--help` o `help`