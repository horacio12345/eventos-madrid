#!/usr/bin/env python3
# scripts/setup.py

"""
Script de configuración inicial completa del sistema
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path

# Añadir el directorio raíz al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def check_python_version():
    """
    Verificar versión de Python
    """
    print("🐍 Verificando versión de Python...")

    if sys.version_info < (3, 11):
        print("❌ Se requiere Python 3.11 o superior")
        print(f"   Versión actual: {sys.version}")
        return False

    print(f"✅ Python {sys.version.split()[0]} - OK")
    return True


def create_directories():
    """
    Crear directorios necesarios
    """
    print("📁 Creando directorios necesarios...")

    directories = [
        "data",
        "data/logs",
        "data/exports",
        "data/temp",
        "logs",
        "nginx",
        "nginx/ssl",
    ]

    for directory in directories:
        path = Path(directory)
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            print(f"   ✅ Creado: {directory}")
        else:
            print(f"   ⚠️  Ya existe: {directory}")


def check_dependencies():
    """
    Verificar dependencias del sistema
    """
    print("📦 Verificando dependencias del sistema...")

    # Verificar que playwright esté instalado
    try:
        import playwright

        print("   ✅ Playwright - Instalado")

        # Verificar browsers de Playwright
        print("🌐 Verificando browsers de Playwright...")
        result = subprocess.run(
            ["python", "-m", "playwright", "install", "chromium"],
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            print("   ✅ Browsers de Playwright - OK")
        else:
            print("   ⚠️  Instalando browsers de Playwright...")
            subprocess.run(["python", "-m", "playwright", "install", "chromium"])
            print("   ✅ Browsers instalados")

    except ImportError:
        print("   ❌ Playwright no instalado")
        print("   Instalar con: pip install playwright")
        return False

    # Verificar otras dependencias críticas
    critical_deps = [
        ("sqlalchemy", "SQLAlchemy"),
        ("fastapi", "FastAPI"),
        ("langchain", "LangChain"),
        ("langgraph", "LangGraph"),
        ("docling", "Docling"),
        ("apscheduler", "APScheduler"),
    ]

    for module, name in critical_deps:
        try:
            __import__(module)
            print(f"   ✅ {name} - Instalado")
        except ImportError:
            print(f"   ❌ {name} - NO INSTALADO")
            print(f"   Instalar con: pip install {module}")
            return False

    return True


def create_env_file():
    """
    Crear archivo .env de ejemplo
    """
    print("⚙️  Creando archivo de configuración...")

    env_example = """# =============================================================================
# CONFIGURACIÓN DEL SISTEMA - Eventos Mayores Madrid
# =============================================================================

# ============= APLICACIÓN =============
APP_NAME="Eventos Mayores Madrid"
DEBUG=false
ENVIRONMENT=production

# ============= BASE DE DATOS =============
DATABASE_URL=sqlite:///./data/database.db

# ============= SEGURIDAD =============
SECRET_KEY=tu_clave_secreta_muy_larga_y_segura_de_al_menos_32_caracteres
ADMIN_USERNAME=admin
ADMIN_PASSWORD=tu_password_seguro

# ============= APIS DE IA =============
# Configurar al menos una de estas APIs:
OPENAI_API_KEY=sk-your-openai-api-key-here
OPENAI_MODEL=gpt-4o-mini

# ANTHROPIC_API_KEY=your-anthropic-api-key-here
# ANTHROPIC_MODEL=claude-3-haiku-20240307

# ============= SCRAPING =============
REQUEST_TIMEOUT=30
MAX_RETRIES=3
PLAYWRIGHT_HEADLESS=true
PLAYWRIGHT_TIMEOUT=30000

# ============= SCHEDULER =============
SCHEDULER_TIMEZONE=Europe/Madrid
DEFAULT_UPDATE_FREQUENCY="0 9 * * 1"

# ============= CORS =============
ALLOWED_ORIGINS=["http://localhost:3000","http://127.0.0.1:3000","https://tu-dominio.com"]

# =============================================================================
# INSTRUCCIONES:
# 1. Renombra este archivo a .env
# 2. Cambia SECRET_KEY por una clave segura de al menos 32 caracteres
# 3. Cambia ADMIN_PASSWORD por una contraseña segura
# 4. Configura al menos OPENAI_API_KEY o ANTHROPIC_API_KEY
# 5. Ajusta ALLOWED_ORIGINS con tu dominio de producción
# =============================================================================
"""

    env_file = Path(".env.example")

    if not env_file.exists():
        with open(env_file, "w", encoding="utf-8") as f:
            f.write(env_example)
        print("   ✅ Archivo .env.example creado")
    else:
        print("   ⚠️  .env.example ya existe")

    # Verificar si existe .env
    if not Path(".env").exists():
        print("   ⚠️  IMPORTANTE: Copia .env.example a .env y configúralo")
        return False
    else:
        print("   ✅ Archivo .env encontrado")
        return True


def initialize_database():
    """
    Inicializar base de datos
    """
    print("🗄️  Inicializando base de datos...")

    try:
        from scripts.init_db import init_database

        init_database()
        print("   ✅ Base de datos inicializada")
        return True
    except Exception as e:
        print(f"   ❌ Error inicializando base de datos: {e}")
        return False


def seed_example_sources():
    """
    Insertar fuentes de ejemplo
    """
    print("🌱 Insertando fuentes de ejemplo...")

    try:
        from scripts.seed_sources import seed_default_sources

        seed_default_sources()
        print("   ✅ Fuentes de ejemplo insertadas")
        return True
    except Exception as e:
        print(f"   ❌ Error insertando fuentes: {e}")
        return False


def create_nginx_config():
    """
    Crear configuración básica de nginx
    """
    print("🌐 Creando configuración de nginx...")

    nginx_config = """# nginx/nginx.conf
# Configuración básica para Eventos Mayores Madrid

events {
    worker_connections 1024;
}

http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;
    
    # Logs
    access_log /var/log/nginx/access.log;
    error_log /var/log/nginx/error.log;
    
    # Configuración básica
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    
    # Límites de upload
    client_max_body_size 10M;
    
    # Compresión
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
    
    upstream backend {
        server backend:8000;
    }
    
    upstream frontend {
        server frontend:3000;
    }
    
    # Servidor principal
    server {
        listen 80;
        server_name tu-dominio.com;  # CAMBIAR POR TU DOMINIO
        
        # Logs específicos
        access_log /var/log/nginx/eventos_access.log;
        error_log /var/log/nginx/eventos_error.log;
        
        # API Backend
        location /api/ {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # Timeouts para scraping largo
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }
        
        # Frontend
        location / {
            proxy_pass http://frontend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
        
        # Archivos estáticos
        location /static/ {
            alias /app/static/;
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
        
        # Health check
        location /health {
            proxy_pass http://backend/api/health;
        }
    }
    
    # Redirigir HTTPS si se configura SSL
    # server {
    #     listen 443 ssl;
    #     server_name tu-dominio.com;
    #     
    #     ssl_certificate /etc/nginx/ssl/cert.pem;
    #     ssl_certificate_key /etc/nginx/ssl/key.pem;
    #     
    #     # Configuración SSL moderna
    #     ssl_protocols TLSv1.2 TLSv1.3;
    #     ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    #     ssl_prefer_server_ciphers off;
    #     
    #     # Resto de configuración igual que HTTP
    # }
}
"""

    nginx_file = Path("nginx/nginx.conf")

    if not nginx_file.exists():
        with open(nginx_file, "w", encoding="utf-8") as f:
            f.write(nginx_config)
        print("   ✅ Configuración nginx creada")
        print("   ⚠️  IMPORTANTE: Edita nginx/nginx.conf y cambia 'tu-dominio.com'")
    else:
        print("   ⚠️  nginx.conf ya existe")


def print_final_instructions():
    """
    Mostrar instrucciones finales
    """
    print(
        """
🎉 ¡CONFIGURACIÓN INICIAL COMPLETADA!

📋 PRÓXIMOS PASOS:

1️⃣  CONFIGURAR VARIABLES DE ENTORNO:
   - Edita el archivo .env
   - Cambia SECRET_KEY por una clave segura
   - Configura ADMIN_PASSWORD
   - Añade tu OPENAI_API_KEY o ANTHROPIC_API_KEY

2️⃣  CONFIGURAR NGINX:
   - Edita nginx/nginx.conf
   - Cambia 'tu-dominio.com' por tu dominio real

3️⃣  EJECUTAR EL SISTEMA:
   Para desarrollo:
     docker-compose up -d

4️⃣  ACCEDER AL SISTEMA:
   - Frontend: http://localhost:3000
   - API: http://localhost:8000
   - Admin: http://localhost:3000/admin

5️⃣  GESTIÓN DEL SISTEMA:
   python scripts/manage_system.py status
   python scripts/manage_system.py scheduler start
   python scripts/test_scraping.py

⚠️  IMPORTANTE PARA PRODUCCIÓN:
   - Configura SSL en nginx
   - Cambia todas las contraseñas por defecto
   - Configura firewall
   - Haz backup de la carpeta /data

🆘 AYUDA:
   python scripts/manage_system.py help
   python scripts/test_scraping.py --help

🎯 ¡YA ESTÁ LISTO PARA USAR!
"""
    )


def main():
    """
    Función principal de configuración
    """
    print("🚀 CONFIGURACIÓN INICIAL - Eventos Mayores Madrid\n")

    steps = [
        ("Verificar Python", check_python_version),
        ("Crear directorios", create_directories),
        ("Verificar dependencias", check_dependencies),
        ("Crear configuración", create_env_file),
        ("Inicializar base de datos", initialize_database),
        ("Insertar fuentes ejemplo", seed_example_sources),
        ("Crear configuración nginx", create_nginx_config),
    ]

    failed_steps = []

    for step_name, step_function in steps:
        try:
            if not step_function():
                failed_steps.append(step_name)
        except Exception as e:
            print(f"❌ Error en {step_name}: {e}")
            failed_steps.append(step_name)
        print()  # Línea en blanco entre pasos

    if failed_steps:
        print(f"⚠️  CONFIGURACIÓN COMPLETADA CON ADVERTENCIAS")
        print(f"   Pasos con problemas: {', '.join(failed_steps)}")
        print(f"   Revisa los mensajes anteriores para más detalles")
    else:
        print("✅ CONFIGURACIÓN COMPLETADA EXITOSAMENTE")

    print_final_instructions()


if __name__ == "__main__":
    main()
