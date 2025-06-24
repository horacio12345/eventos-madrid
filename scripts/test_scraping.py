#!/usr/bin/env python3
# scripts/test_scraping.py

"""
Script para testear el scraping de una fuente específica
"""
import sys
import os
import asyncio
import json
from datetime import datetime

# Añadir el directorio raíz al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.core.database import SessionLocal
from backend.services.source_manager import SourceManager
from backend.scraping.engine import ScrapingEngine

async def test_source_scraping(source_id: int = None, source_name: str = None):
    """
    Testear scraping de una fuente específica
    """
    print("🧪 Iniciando test de scraping...")
    
    db = SessionLocal()
    try:
        source_manager = SourceManager(db)
        
        # Obtener fuente
        if source_id:
            fuente = source_manager.get_source(source_id)
            if not fuente:
                print(f"❌ No se encontró fuente con ID: {source_id}")
                return
        elif source_name:
            fuentes = source_manager.get_all_sources()
            fuente = next((f for f in fuentes if source_name.lower() in f.nombre.lower()), None)
            if not fuente:
                print(f"❌ No se encontró fuente con nombre que contenga: {source_name}")
                return
        else:
            # Mostrar fuentes disponibles
            print("\n📋 Fuentes disponibles:")
            fuentes = source_manager.get_all_sources()
            for f in fuentes:
                estado = "🟢 ACTIVA" if f.activa else "🔴 INACTIVA"
                print(f"  ID: {f.id} | {estado} | {f.nombre}")
            print("\nUso: python test_scraping.py <ID> o python test_scraping.py --name <nombre>")
            return
        
        print(f"\n🎯 Testeando fuente: {fuente.nombre}")
        print(f"   URL: {fuente.url}")
        print(f"   Tipo: {fuente.tipo}")
        print(f"   Estado: {'🟢 ACTIVA' if fuente.activa else '🔴 INACTIVA'}")
        
        # Crear engine y testear
        engine = ScrapingEngine()
        
        configuracion_test = {
            "url": fuente.url,
            "tipo": fuente.tipo,
            "schema_extraccion": fuente.schema_extraccion,
            "mapeo_campos": fuente.mapeo_campos,
            "configuracion_scraping": fuente.configuracion_scraping
        }
        
        print("\n⏳ Ejecutando test de extracción...")
        inicio = datetime.now()
        
        resultado = await engine.test_fuente(configuracion_test)
        
        fin = datetime.now()
        tiempo_total = (fin - inicio).total_seconds()
        
        # Mostrar resultados
        print(f"\n📊 RESULTADOS DEL TEST:")
        print(f"   ⏱️  Tiempo: {tiempo_total:.2f} segundos")
        print(f"   📈 Estado: {resultado['estado']}")
        
        if resultado['estado'] == 'success':
            print(f"   🎉 Eventos encontrados: {resultado['eventos_encontrados']}")
            
            if resultado['preview_eventos']:
                print(f"\n📋 PREVIEW DE EVENTOS (primeros 3):")
                for i, evento in enumerate(resultado['preview_eventos'], 1):
                    print(f"\n   📌 Evento {i}:")
                    print(f"      Título: {evento.get('titulo', 'Sin título')}")
                    print(f"      Fecha: {evento.get('fecha_inicio', 'Sin fecha')}")
                    print(f"      Precio: {evento.get('precio', 'Sin precio')}")
                    print(f"      Ubicación: {evento.get('ubicacion', 'Sin ubicación')}")
                    if evento.get('descripcion'):
                        desc = evento['descripcion'][:100] + "..." if len(evento['descripcion']) > 100 else evento['descripcion']
                        print(f"      Descripción: {desc}")
            else:
                print(f"   ⚠️  No se encontraron eventos")
        else:
            print(f"   ❌ Error: {resultado.get('error', 'Error desconocido')}")
            if resultado.get('errores'):
                print(f"   📝 Detalles:")
                for error in resultado['errores']:
                    print(f"      - {error}")
        
        # Guardar resultado completo en archivo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"test_results_{fuente.id}_{timestamp}.json"
        
        resultado_completo = {
            "fuente": {
                "id": fuente.id,
                "nombre": fuente.nombre,
                "url": fuente.url,
                "tipo": fuente.tipo
            },
            "test_timestamp": inicio.isoformat(),
            "tiempo_ejecucion": tiempo_total,
            "resultado": resultado
        }
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(resultado_completo, f, indent=2, ensure_ascii=False, default=str)
            print(f"\n💾 Resultado completo guardado en: {filename}")
        except Exception as e:
            print(f"\n⚠️  No se pudo guardar archivo: {e}")
        
    except Exception as e:
        print(f"❌ Error durante el test: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

def print_help():
    """
    Mostrar ayuda del script
    """
    print("""
🧪 TEST DE SCRAPING - Eventos Mayores Madrid

USO:
  python test_scraping.py                    # Mostrar fuentes disponibles
  python test_scraping.py <ID>              # Testear fuente por ID
  python test_scraping.py --name <nombre>   # Testear fuente por nombre

EJEMPLOS:
  python test_scraping.py 1
  python test_scraping.py --name "ayuntamiento"
  python test_scraping.py --name "madrid"

DESCRIPCIÓN:
  Este script permite testear la configuración de scraping de una fuente
  específica sin guardar los datos en la base de datos. Útil para:
  
  - Verificar que los selectores CSS funcionan
  - Probar configuraciones antes de activar una fuente
  - Debuggear problemas de extracción
  - Ver preview de eventos que se extraerían
  
SALIDA:
  - Resultado del test en consola
  - Archivo JSON con resultado completo
  - Preview de primeros 3 eventos encontrados
""")

async def main():
    """
    Función principal del script
    """
    args = sys.argv[1:]
    
    if not args or args[0] in ['-h', '--help', 'help']:
        print_help()
        return
    
    if args[0] == '--name' and len(args) > 1:
        await test_source_scraping(source_name=args[1])
    elif args[0].isdigit():
        await test_source_scraping(source_id=int(args[0]))
    else:
        print("❌ Parámetro inválido. Usa --help para ver la ayuda.")

if __name__ == "__main__":
    asyncio.run(main())