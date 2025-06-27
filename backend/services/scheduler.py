# backend/services/scheduler.py

"""
Scheduler simple para tareas de scraping sin dependencias externas complejas
"""
import asyncio
import threading
from datetime import datetime, timedelta
from typing import Callable, Dict, List, Optional

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.orm import Session

from backend.core import FuenteWeb, get_db, get_settings

from .source_manager import SourceManager

settings = get_settings()


class ScrapingScheduler:
    """
    Scheduler simple para ejecutar scraping de fuentes automáticamente
    """

    def __init__(self, scraping_engine=None):
        self.scheduler = BackgroundScheduler(timezone=settings.scheduler_timezone)
        self.scraping_engine = scraping_engine
        self.is_running = False
        self._job_callbacks: Dict[str, Callable] = {}

    def start(self):
        """
        Iniciar el scheduler
        """
        if not self.is_running:
            self.scheduler.start()
            self.is_running = True
            print(f"Scheduler iniciado en timezone: {settings.scheduler_timezone}")

            # Cargar trabajos existentes
            self._load_existing_jobs()

    def stop(self):
        """
        Detener el scheduler
        """
        if self.is_running:
            self.scheduler.shutdown()
            self.is_running = False
            print("Scheduler detenido")

    def add_source_job(self, source_id: int, cron_expression: str = None) -> bool:
        """
        Añadir trabajo de scraping para una fuente
        """
        try:
            with next(get_db()) as db:
                source_manager = SourceManager(db)
                fuente = source_manager.get_source(source_id)

                if not fuente or not fuente.activa:
                    return False

                # Usar expresión cron de la fuente o la por defecto
                cron_expr = (
                    cron_expression
                    or fuente.frecuencia_actualizacion
                    or settings.default_update_frequency
                )

                # Parsear expresión cron
                trigger = self._parse_cron_expression(cron_expr)

                # ID único para el trabajo
                job_id = f"scraping_fuente_{source_id}"

                # Eliminar trabajo existente si existe
                if self.scheduler.get_job(job_id):
                    self.scheduler.remove_job(job_id)

                # Añadir nuevo trabajo
                self.scheduler.add_job(
                    func=self._execute_source_scraping,
                    trigger=trigger,
                    id=job_id,
                    args=[source_id],
                    name=f"Scraping: {fuente.nombre}",
                    replace_existing=True,
                    max_instances=1,  # Evitar ejecuciones múltiples simultáneas
                )

                print(
                    f"Trabajo programado para fuente '{fuente.nombre}' con cron: {cron_expr}"
                )
                return True

        except Exception as e:
            print(f"Error añadiendo trabajo para fuente {source_id}: {e}")
            return False

    def remove_source_job(self, source_id: int) -> bool:
        """
        Eliminar trabajo de scraping para una fuente
        """
        try:
            job_id = f"scraping_fuente_{source_id}"

            if self.scheduler.get_job(job_id):
                self.scheduler.remove_job(job_id)
                print(f"Trabajo eliminado para fuente {source_id}")
                return True

            return False

        except Exception as e:
            print(f"Error eliminando trabajo para fuente {source_id}: {e}")
            return False

    def trigger_immediate_scraping(self, source_id: Optional[int] = None) -> bool:
        """
        Ejecutar scraping inmediatamente para una fuente o todas
        """
        try:
            if source_id:
                # Ejecutar fuente específica
                self._execute_source_scraping(source_id)
            else:
                # Ejecutar todas las fuentes activas
                with next(get_db()) as db:
                    source_manager = SourceManager(db)
                    fuentes_activas = source_manager.get_active_sources()

                    for fuente in fuentes_activas:
                        self._execute_source_scraping(fuente.id)

            return True

        except Exception as e:
            print(f"Error en scraping inmediato: {e}")
            return False

    def _execute_source_scraping(self, source_id: int):
        """
        Ejecutar scraping para una fuente específica
        """
        try:
            print(f"Iniciando scraping para fuente {source_id}")

            if self.scraping_engine:
                # Ejecutar de forma asíncrona si tenemos el engine
                asyncio.run(self._async_scraping_wrapper(source_id))
            else:
                print(f"No hay scraping engine configurado para fuente {source_id}")

        except Exception as e:
            print(f"Error ejecutando scraping para fuente {source_id}: {e}")

            # Actualizar estado de error en la fuente
            try:
                with next(get_db()) as db:
                    source_manager = SourceManager(db)
                    source_manager.update_source_status(source_id, "error", str(e))
            except Exception:
                pass

    async def _async_scraping_wrapper(self, source_id: int):
        """
        Wrapper asíncrono para ejecutar scraping
        """
        try:
            result = await self.scraping_engine.execute_scraping(source_id)
            print(f"Scraping completado para fuente {source_id}: {result}")

        except Exception as e:
            print(f"Error en scraping asíncrono para fuente {source_id}: {e}")
            raise

    def _load_existing_jobs(self):
        """
        Cargar trabajos existentes desde la base de datos
        """
        try:
            with next(get_db()) as db:
                source_manager = SourceManager(db)
                fuentes_activas = source_manager.get_active_sources()

                for fuente in fuentes_activas:
                    self.add_source_job(fuente.id)

                print(f"Cargados {len(fuentes_activas)} trabajos de scraping")

        except Exception as e:
            print(f"Error cargando trabajos existentes: {e}")

    def _parse_cron_expression(self, cron_expr: str) -> CronTrigger:
        """
        Parsear expresión cron a trigger de APScheduler
        """
        try:
            # Formato: "minute hour day month day_of_week"
            # Ejemplo: "0 9 * * 1" = Lunes a las 9:00
            parts = cron_expr.strip().split()

            if len(parts) != 5:
                raise ValueError(f"Expresión cron inválida: {cron_expr}")

            minute, hour, day, month, day_of_week = parts

            return CronTrigger(
                minute=minute, hour=hour, day=day, month=month, day_of_week=day_of_week
            )

        except Exception as e:
            print(f"Error parseando cron '{cron_expr}': {e}")
            # Fallback a expresión por defecto
            return CronTrigger(minute=0, hour=9, day_of_week="mon")  # Lunes 9:00

    def get_scheduled_jobs(self) -> List[Dict]:
        """
        Obtener lista de trabajos programados
        """
        jobs = []

        for job in self.scheduler.get_jobs():
            if job.id.startswith("scraping_fuente_"):
                source_id = int(job.id.replace("scraping_fuente_", ""))

                jobs.append(
                    {
                        "source_id": source_id,
                        "job_id": job.id,
                        "name": job.name,
                        "next_run": (
                            job.next_run_time.isoformat() if job.next_run_time else None
                        ),
                        "trigger": str(job.trigger),
                    }
                )

        return jobs

    def update_source_schedule(self, source_id: int, new_cron: str) -> bool:
        """
        Actualizar programación de una fuente
        """
        try:
            # Eliminar trabajo actual
            self.remove_source_job(source_id)

            # Actualizar en base de datos
            with next(get_db()) as db:
                source_manager = SourceManager(db)
                source_manager.update_source(
                    source_id, {"frecuencia_actualizacion": new_cron}
                )

            # Añadir nuevo trabajo
            return self.add_source_job(source_id, new_cron)

        except Exception as e:
            print(f"Error actualizando programación de fuente {source_id}: {e}")
            return False

    def get_scheduler_status(self) -> Dict:
        """
        Obtener estado del scheduler
        """
        return {
            "running": self.is_running,
            "timezone": settings.scheduler_timezone,
            "total_jobs": len(self.scheduler.get_jobs()),
            "scraping_jobs": len(
                [
                    j
                    for j in self.scheduler.get_jobs()
                    if j.id.startswith("scraping_fuente_")
                ]
            ),
            "next_runs": [
                {
                    "job_name": job.name,
                    "next_run": (
                        job.next_run_time.isoformat() if job.next_run_time else None
                    ),
                }
                for job in self.scheduler.get_jobs()
                if job.next_run_time
            ][
                :5
            ],  # Solo próximas 5 ejecuciones
        }


# ============= FUNCIONES GLOBALES =============

# Instancia global del scheduler
_scheduler_instance: Optional[ScrapingScheduler] = None


def get_scheduler() -> ScrapingScheduler:
    """
    Obtener instancia global del scheduler
    """
    global _scheduler_instance

    if _scheduler_instance is None:
        _scheduler_instance = ScrapingScheduler()

    return _scheduler_instance


def start_scheduler(scraping_engine=None):
    """
    Iniciar scheduler global
    """
    scheduler = get_scheduler()

    if scraping_engine:
        scheduler.scraping_engine = scraping_engine

    scheduler.start()


def stop_scheduler():
    """
    Detener scheduler global
    """
    scheduler = get_scheduler()
    scheduler.stop()
