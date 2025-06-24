#!/usr/bin/env python3
# scripts/manage_system.py

"""
Script para gestión y mantenimiento del sistema
"""
import sys
import os
import asyncio
from datetime import datetime, timedelta

# Añadir el directorio raíz al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.core.database import SessionLocal
from backend.core.models import Evento, FuenteWeb, LogScraping, Configuracion
from backend.services.scheduler import get_scheduler, start_scheduler, stop_scheduler
from backend.services.source_manager import SourceManager
from backend.scraping.engine import ScrapingEngine

class SystemManager:
    """
    Gestor principal del sistema
    """
    
    def __init__(self):
        self.db = SessionLocal()
    
    def __del__(self):
        if hasattr(self, 'db'):
            self.db.close()
    
    def status(self):
        """
        Mostrar estado general del sistema
        """
        print("📊 ESTADO DEL SISTEMA - Eventos Mayores Madrid\n")
        
        try:
            # Estadísticas generales
            total_eventos = self.db.query(Evento).count()
            eventos_activos = self.db.query(Evento).filter(Evento.activo == True).count()
            total_fuentes = self.db.query(FuenteWeb).count()
            fuentes_activas = self.db.query(FuenteWeb).filter(FuenteWeb.activa == True).count()
            
            print(f"🎭 EVENTOS:")
            print(f"   Total: {total_eventos}")
            print(f"   Activos: {eventos_activos}")
            print(f"   Inactivos: {total_eventos - eventos_activos}")
            
            print(f"\n🌐 FUENTES:")
            print(f"   Total: {total_fuentes}")
            print(f"   Activas: {fuentes_activas}")
            print(f"   Inactivas: {total_fuentes - fuentes_activas}")
            
            # Últimos logs
            recent_logs = self.db.query(LogScraping).order_by(
                LogScraping.fecha_inicio.desc()
            ).limit(5).all()
            
            print(f"\n📋 ÚLTIMOS SCRAPINGS:")
            if recent_logs:
                for log in recent_logs:
                    estado_emoji = "✅" if log.estado == "success" else "❌" if log.estado == "error" else "⏳"
                    fecha = log.fecha_inicio.strftime("%d/%m %H:%M")
                    print(f"   {estado_emoji} {fecha} | {log.fuente_nombre} | {log.eventos_extraidos or 0} eventos")
            else:
                print("   No hay logs de scraping")
            
            # Estado del scheduler
            try:
                scheduler = get_scheduler()
                scheduler_status = scheduler.get_scheduler_status()
                print(f"\n⏰ SCHEDULER:")
                print(f"   Estado: {'🟢 ACTIVO' if scheduler_status['running'] else '🔴 INACTIVO'}")
                print(f"   Jobs totales: {scheduler_status['total_jobs']}")
                print(f"   Jobs de scraping: {scheduler_status['scraping_jobs']}")
            except Exception:
                print(f"\n⏰ SCHEDULER: 🔴 NO DISPONIBLE")
            
        except Exception as e:
            print(f"❌ Error obteniendo estado: {e}")
    
    def cleanup_old_data(self, days: int = 30):
        """
        Limpiar datos antiguos del sistema
        """
        print(f"🧹 Limpiando datos anteriores a {days} días...")
        
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            # Limpiar eventos viejos inactivos
            old_events = self.db.query(Evento).filter(
                Evento.activo == False,
                Evento.ultima_actualizacion < cutoff_date
            ).count()
            
            if old_events > 0:
                self.db.query(Evento).filter(
                    Evento.activo == False,
                    Evento.ultima_actualizacion < cutoff_date
                ).delete()
                print(f"   ✅ Eliminados {old_events} eventos inactivos antiguos")
            
            # Limpiar logs antiguos
            old_logs = self.db.query(LogScraping).filter(
                LogScraping.fecha_inicio < cutoff_date
            ).count()
            
            if old_logs > 0:
                self.db.query(LogScraping).filter(
                    LogScraping.fecha_inicio < cutoff_date
                ).delete()
                print(f"   ✅ Eliminados {old_logs} logs antiguos")
            
            self.db.commit()
            print("   🎉 Limpieza completada")
            
        except Exception as e:
            self.db.rollback()
            print(f"   ❌ Error en limpieza: {e}")
    
    def run_scraping(self, source_id: int = None):
        """
        Ejecutar scraping manualmente
        """
        async def _run():
            try:
                engine = ScrapingEngine()
                print("⏳ Ejecutando scraping...")
                
                if source_id:
                    print(f"   🎯 Fuente específica: ID {source_id}")
                else:
                    print("   🌐 Todas las fuentes activas")
                
                resultado = await engine.execute_scraping(source_id)
                
                print(f"\n📊 RESULTADO:")
                print(f"   Total ejecutadas: {resultado['total_ejecutadas']}")
                print(f"   Exitosas: {resultado['exitosas']}")
                print(f"   Con errores: {resultado['errores']}")
                
                for detalle in resultado['detalles']:
                    estado_emoji = "✅" if detalle['estado'] == 'success' else "❌"
                    print(f"   {estado_emoji} {detalle['fuente_nombre']}")
                    if detalle['estado'] == 'success':
                        print(f"      Nuevos: {detalle.get('eventos_nuevos', 0)}")
                        print(f"      Actualizados: {detalle.get('eventos_actualizados', 0)}")
                    else:
                        print(f"      Error: {detalle.get('error', 'Desconocido')}")
                
            except Exception as e:
                print(f"❌ Error ejecutando scraping: {e}")
        
        asyncio.run(_run())
    
    def scheduler_control(self, action: str):
        """
        Controlar el scheduler (start/stop/status)
        """
        try:
            scheduler = get_scheduler()
            
            if action == "start":
                print("⏰ Iniciando scheduler...")
                engine = ScrapingEngine()
                start_scheduler(engine)
                print("   ✅ Scheduler iniciado")
                
            elif action == "stop":
                print("⏰ Deteniendo scheduler...")
                stop_scheduler()
                print("   ✅ Scheduler detenido")
                
            elif action == "status":
                status = scheduler.get_scheduler_status()
                print("⏰ ESTADO DEL SCHEDULER:")
                print(f"   Running: {'🟢 SÍ' if status['running'] else '🔴 NO'}")
                print(f"   Jobs totales: {status['total_jobs']}")
                print(f"   Jobs de scraping: {status['scraping_jobs']}")
                
                if status['next_runs']:
                    print("\n   📅 Próximas ejecuciones:")
                    for job in status['next_runs'][:3]:
                        print(f"      - {job['job_name']}: {job['next_run']}")
                        
            elif action == "reload":
                print("⏰ Recargando trabajos del scheduler...")
                stop_scheduler()
                engine = ScrapingEngine()
                start_scheduler(engine)
                print("   ✅ Scheduler recargado")
                
            else:
                print("❌ Acción no válida. Use: start, stop, status, reload")
                
        except Exception as e:
            print(f"❌ Error controlando scheduler: {e}")
    
    def list_sources(self):
        """
        Listar todas las fuentes
        """
        print("🌐 FUENTES CONFIGURADAS:\n")
        
        try:
            source_manager = SourceManager(self.db)
            fuentes = source_manager.get_all_sources()
            
            if not fuentes:
                print("   No hay fuentes configuradas")
                return
            
            for fuente in fuentes:
                estado = "🟢 ACTIVA" if fuente.activa else "🔴 INACTIVA"
                ultimo_estado = ""
                if fuente.ultimo_estado == "success":
                    ultimo_estado = "✅"
                elif fuente.ultimo_estado == "error":
                    ultimo_estado = "❌"
                else:
                    ultimo_estado = "⏳"
                
                print(f"📌 ID: {fuente.id} | {estado} | {ultimo_estado}")
                print(f"   Nombre: {fuente.nombre}")
                print(f"   URL: {fuente.url}")
                print(f"   Tipo: {fuente.tipo}")
                if fuente.ultima_ejecucion:
                    print(f"   Última ejecución: {fuente.ultima_ejecucion.strftime('%d/%m/%Y %H:%M')}")
                if fuente.eventos_encontrados_ultima_ejecucion:
                    print(f"   Eventos última vez: {fuente.eventos_encontrados_ultima_ejecucion}")
                print()
                
        except Exception as e:
            print(f"❌ Error listando fuentes: {e}")

def print_help():
    """
    Mostrar ayuda del script
    """
    print("""
🛠️  GESTOR DEL SISTEMA - Eventos Mayores Madrid

USO:
  python manage_system.py <comando> [opciones]

COMANDOS:
  status                    # Mostrar estado general del sistema
  cleanup [días]           # Limpiar datos antiguos (defecto: 30 días)
  scraping [ID_fuente]     # Ejecutar scraping manual
  scheduler <acción>       # Controlar scheduler (start/stop/status/reload)
  sources                  # Listar todas las fuentes
  help                     # Mostrar esta ayuda

EJEMPLOS:
  python manage_system.py status
  python manage_system.py cleanup 60
  python manage_system.py scraping 1
  python manage_system.py scheduler start
  python manage_system.py sources

DESCRIPCIÓN DE COMANDOS:

📊 status:
    Muestra estadísticas generales, eventos, fuentes, últimos logs
    y estado del scheduler.

🧹 cleanup [días]:
    Elimina eventos inactivos y logs anteriores al número de días
    especificado (por defecto 30 días).

⚡ scraping [ID]:
    Ejecuta scraping manualmente. Si no se especifica ID, ejecuta
    todas las fuentes activas.

⏰ scheduler <acción>:
    - start: Inicia el programador automático
    - stop: Detiene el programador
    - status: Muestra estado y próximas ejecuciones
    - reload: Reinicia el programador cargando nuevas configuraciones

🌐 sources:
    Lista todas las fuentes configuradas con su estado y estadísticas.
""")

def main():
    """
    Función principal del script
    """
    args = sys.argv[1:]
    
    if not args or args[0] in ['-h', '--help', 'help']:
        print_help()
        return
    
    comando = args[0].lower()
    manager = SystemManager()
    
    try:
        if comando == "status":
            manager.status()
            
        elif comando == "cleanup":
            days = int(args[1]) if len(args) > 1 and args[1].isdigit() else 30
            manager.cleanup_old_data(days)
            
        elif comando == "scraping":
            source_id = int(args[1]) if len(args) > 1 and args[1].isdigit() else None
            manager.run_scraping(source_id)
            
        elif comando == "scheduler":
            if len(args) < 2:
                print("❌ Especifica una acción: start, stop, status, reload")
                return
            manager.scheduler_control(args[1])
            
        elif comando == "sources":
            manager.list_sources()
            
        else:
            print(f"❌ Comando desconocido: {comando}")
            print("Use 'help' para ver comandos disponibles")
            
    except KeyboardInterrupt:
        print("\n⏹️  Operación cancelada por el usuario")
    except Exception as e:
        print(f"❌ Error ejecutando comando: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()