// app/admin/dashboard/page.tsx

'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { 
  CalendarIcon,
  GlobeAltIcon,
  CheckCircleIcon,
  XCircleIcon,
  ClockIcon,
  PlayIcon,
  ArrowPathIcon,
  ChartBarIcon
} from '@heroicons/react/24/outline';
import { useEventos, useFuentes, useLogs } from '@/lib/api';
import { api } from '@/lib/api';
import { formatDateTime, getCategoriaConfig, formatPrice } from '@/lib/utils';
import LoadingSpinner from '@/components/LoadingSpinner';
import Alert from '@/components/Alert';

export default function DashboardPage() {
  const [triggeringUpdate, setTriggeringUpdate] = useState(false);
  const [updateMessage, setUpdateMessage] = useState('');

  // Cargar datos
  const { data: eventos, loading: eventosLoading, refetch: refetchEventos } = useEventos();
  const { data: fuentes, loading: fuentesLoading, refetch: refetchFuentes } = useFuentes();
  const { data: logs, loading: logsLoading } = useLogs();

  // Estadísticas calculadas
  const stats = {
    totalEventos: eventos?.length || 0,
    eventosActivos: eventos?.filter(e => e.activo).length || 0,
    totalFuentes: fuentes?.length || 0,
    fuentesActivas: fuentes?.filter(f => f.activa).length || 0,
    ultimoScraping: logs?.[0]?.fecha_inicio || null,
    scrapingsExitosos: logs?.filter(l => l.estado === 'success').length || 0,
    scrapingsConError: logs?.filter(l => l.estado === 'error').length || 0
  };

  // Categorías con eventos
  const eventosPorCategoria = eventos?.reduce((acc, evento) => {
    const categoria = evento.categoria;
    acc[categoria] = (acc[categoria] || 0) + 1;
    return acc;
  }, {} as Record<string, number>) || {};

  // Trigger scraping manual
  const handleTriggerScraping = async () => {
    setTriggeringUpdate(true);
    setUpdateMessage('');
    
    try {
      const result = await api.admin.scraping.trigger();
      setUpdateMessage(`Scraping ejecutado: ${result.exitosas} exitosos, ${result.errores} errores`);
      
      // Refrescar datos después de 2 segundos
      setTimeout(() => {
        refetchEventos();
        refetchFuentes();
      }, 2000);
      
    } catch (error) {
      setUpdateMessage(`Error: ${error instanceof Error ? error.message : 'Error desconocido'}`);
    } finally {
      setTriggeringUpdate(false);
    }
  };

  return (
    <div className="container-wide">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Dashboard</h1>
        <p className="text-gray-600">
          Panel de control del sistema de eventos para mayores
        </p>
      </div>

      {/* Mensaje de actualización */}
      {updateMessage && (
        <div className="mb-6">
          <Alert
            type={updateMessage.includes('Error') ? 'error' : 'success'}
            message={updateMessage}
            dismissible
            onDismiss={() => setUpdateMessage('')}
          />
        </div>
      )}

      {/* Estadísticas principales */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {/* Total Eventos */}
        <div className="bg-white rounded-lg shadow-card p-6 border border-gray-100">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <CalendarIcon className="h-8 w-8 text-primary-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Total Eventos</p>
              <p className="text-2xl font-bold text-gray-900">
                {eventosLoading ? <LoadingSpinner size="sm" /> : stats.totalEventos}
              </p>
            </div>
          </div>
        </div>

        {/* Eventos Activos */}
        <div className="bg-white rounded-lg shadow-card p-6 border border-gray-100">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <CheckCircleIcon className="h-8 w-8 text-green-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Eventos Activos</p>
              <p className="text-2xl font-bold text-gray-900">
                {eventosLoading ? <LoadingSpinner size="sm" /> : stats.eventosActivos}
              </p>
            </div>
          </div>
        </div>

        {/* Total Fuentes */}
        <div className="bg-white rounded-lg shadow-card p-6 border border-gray-100">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <GlobeAltIcon className="h-8 w-8 text-blue-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Total Fuentes</p>
              <p className="text-2xl font-bold text-gray-900">
                {fuentesLoading ? <LoadingSpinner size="sm" /> : stats.totalFuentes}
              </p>
            </div>
          </div>
        </div>

        {/* Fuentes Activas */}
        <div className="bg-white rounded-lg shadow-card p-6 border border-gray-100">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <PlayIcon className="h-8 w-8 text-purple-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Fuentes Activas</p>
              <p className="text-2xl font-bold text-gray-900">
                {fuentesLoading ? <LoadingSpinner size="sm" /> : stats.fuentesActivas}
              </p>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        {/* Acciones rápidas */}
        <div className="bg-white rounded-lg shadow-card p-6 border border-gray-100">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Acciones Rápidas</h3>
          <div className="space-y-3">
            <button
              onClick={handleTriggerScraping}
              disabled={triggeringUpdate}
              className="w-full btn btn-primary justify-start"
            >
              {triggeringUpdate ? (
                <LoadingSpinner size="sm" />
              ) : (
                <ArrowPathIcon className="h-5 w-5" />
              )}
              <span className="ml-2">
                {triggeringUpdate ? 'Ejecutando scraping...' : 'Ejecutar Scraping Manual'}
              </span>
            </button>

            <Link href="/admin/fuentes" className="w-full btn btn-outline justify-start">
              <GlobeAltIcon className="h-5 w-5" />
              <span className="ml-2">Gestionar Fuentes</span>
            </Link>

            <Link href="/admin/logs" className="w-full btn btn-outline justify-start">
              <ChartBarIcon className="h-5 w-5" />
              <span className="ml-2">Ver Logs del Sistema</span>
            </Link>
          </div>
        </div>

        {/* Estado del último scraping */}
        <div className="bg-white rounded-lg shadow-card p-6 border border-gray-100">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Estado del Sistema</h3>
          <div className="space-y-4">
            {logsLoading ? (
              <LoadingSpinner size="sm" text="Cargando logs..." />
            ) : (
              <>
                {stats.ultimoScraping && (
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-500">Último scraping:</span>
                    <span className="text-sm font-medium text-gray-900">
                      {formatDateTime(stats.ultimoScraping)}
                    </span>
                  </div>
                )}
                
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-500">Scrapings exitosos:</span>
                  <span className="text-sm font-medium text-green-600">
                    {stats.scrapingsExitosos}
                  </span>
                </div>
                
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-500">Scrapings con error:</span>
                  <span className="text-sm font-medium text-red-600">
                    {stats.scrapingsConError}
                  </span>
                </div>
              </>
            )}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Eventos por categoría */}
        <div className="bg-white rounded-lg shadow-card p-6 border border-gray-100">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Eventos por Categoría</h3>
          {eventosLoading ? (
            <LoadingSpinner size="sm" />
          ) : (
            <div className="space-y-3">
              {Object.entries(eventosPorCategoria).map(([categoria, count]) => {
                const config = getCategoriaConfig(categoria as any);
                return (
                  <div key={categoria} className="flex items-center justify-between">
                    <div className="flex items-center">
                      <span className="text-lg mr-2">{config.emoji}</span>
                      <span className="text-sm text-gray-700">{categoria}</span>
                    </div>
                    <span className="text-sm font-medium text-gray-900">{count}</span>
                  </div>
                );
              })}
              {Object.keys(eventosPorCategoria).length === 0 && (
                <p className="text-sm text-gray-500 text-center py-4">
                  No hay eventos disponibles
                </p>
              )}
            </div>
          )}
        </div>

        {/* Estado de fuentes */}
        <div className="bg-white rounded-lg shadow-card p-6 border border-gray-100">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Estado de Fuentes</h3>
          {fuentesLoading ? (
            <LoadingSpinner size="sm" />
          ) : (
            <div className="space-y-3">
              {fuentes?.slice(0, 5).map(fuente => (
                <div key={fuente.id} className="flex items-center justify-between">
                  <div className="flex items-center">
                    <div className={`w-3 h-3 rounded-full mr-3 ${
                      fuente.activa 
                        ? fuente.ultimo_estado === 'success' ? 'bg-green-500' : 'bg-red-500'
                        : 'bg-gray-400'
                    }`} />
                    <span className="text-sm text-gray-700 truncate max-w-40">
                      {fuente.nombre}
                    </span>
                  </div>
                  <span className="text-xs text-gray-500">
                    {fuente.eventos_encontrados_ultima_ejecucion || 0} eventos
                  </span>
                </div>
              ))}
              {fuentes && fuentes.length === 0 && (
                <p className="text-sm text-gray-500 text-center py-4">
                  No hay fuentes configuradas
                </p>
              )}
              {fuentes && fuentes.length > 5 && (
                <Link 
                  href="/admin/fuentes" 
                  className="block text-sm text-primary-600 hover:text-primary-800 text-center pt-2"
                >
                  Ver todas las fuentes →
                </Link>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}