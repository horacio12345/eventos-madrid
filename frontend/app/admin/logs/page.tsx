// app/admin/logs/page.tsx

'use client';

import { useState } from 'react';
import { 
  FunnelIcon,
  ArrowPathIcon,
  CheckCircleIcon,
  XCircleIcon,
  ClockIcon,
  ChevronDownIcon,
  ChevronUpIcon,
  DocumentTextIcon
} from '@heroicons/react/24/outline';
import { useLogs, useFuentes } from '@/lib/api';
import { formatDateTime, formatDuration } from '@/lib/utils';
import type { LogScraping } from '@/lib/types';
import LoadingSpinner from '@/components/LoadingSpinner';
import Alert from '@/components/Alert';

export default function LogsPage() {
  const [selectedFuente, setSelectedFuente] = useState<number | undefined>(undefined);
  const [expandedLog, setExpandedLog] = useState<number | null>(null);
  
  const { data: logs, loading: logsLoading, error: logsError, refetch } = useLogs(selectedFuente);
  const { data: fuentes } = useFuentes();

  const getStatusIcon = (estado: string) => {
    switch (estado) {
      case 'success':
        return <CheckCircleIcon className="h-5 w-5 text-green-500" />;
      case 'error':
        return <XCircleIcon className="h-5 w-5 text-red-500" />;
      case 'running':
        return <ClockIcon className="h-5 w-5 text-yellow-500 animate-spin" />;
      default:
        return <ClockIcon className="h-5 w-5 text-gray-400" />;
    }
  };

  const getStatusBadge = (estado: string) => {
    const classes = {
      success: 'bg-green-100 text-green-800 border-green-200',
      error: 'bg-red-100 text-red-800 border-red-200',
      running: 'bg-yellow-100 text-yellow-800 border-yellow-200',
      pending: 'bg-gray-100 text-gray-800 border-gray-200'
    };

    const labels = {
      success: 'Exitoso',
      error: 'Error',
      running: 'Ejecutando',
      pending: 'Pendiente'
    };

    return (
      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${classes[estado as keyof typeof classes] || classes.pending}`}>
        {labels[estado as keyof typeof labels] || estado}
      </span>
    );
  };

  return (
    <div className="container-wide">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Logs del Sistema</h1>
        <p className="text-gray-600">
          Historial de ejecuciones de scraping y estado del sistema
        </p>
      </div>

      {/* Filtros */}
      <div className="bg-white rounded-lg shadow-card p-4 mb-6 border border-gray-200">
        <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center">
          <div className="flex items-center gap-2">
            <FunnelIcon className="h-5 w-5 text-gray-400" />
            <label className="text-sm font-medium text-gray-700">Filtrar por fuente:</label>
          </div>
          
          <select
            value={selectedFuente || ''}
            onChange={(e) => setSelectedFuente(e.target.value ? parseInt(e.target.value) : undefined)}
            className="select w-auto min-w-48"
          >
            <option value="">Todas las fuentes</option>
            {fuentes?.map(fuente => (
              <option key={fuente.id} value={fuente.id}>
                {fuente.nombre}
              </option>
            ))}
          </select>

          <button
            onClick={refetch}
            disabled={logsLoading}
            className="btn btn-outline btn-sm ml-auto"
          >
            <ArrowPathIcon className={`h-4 w-4 mr-2 ${logsLoading ? 'animate-spin' : ''}`} />
            Actualizar
          </button>
        </div>
      </div>

      {/* Lista de logs */}
      {logsLoading ? (
        <div className="text-center py-12">
          <LoadingSpinner size="lg" text="Cargando logs..." />
        </div>
      ) : logsError ? (
        <Alert type="error" message={logsError} />
      ) : (
        <div className="bg-white shadow-card rounded-lg border border-gray-200">
          {logs && logs.length > 0 ? (
            <div className="divide-y divide-gray-200">
              {logs.map((log) => (
                <div key={log.id} className="p-6">
                  <div className="flex items-start justify-between">
                    <div className="flex items-start space-x-3 flex-1">
                      <div className="flex-shrink-0 mt-1">
                        {getStatusIcon(log.estado)}
                      </div>
                      
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-3 mb-2">
                          <h3 className="text-sm font-medium text-gray-900 truncate">
                            {log.fuente_nombre}
                          </h3>
                          {getStatusBadge(log.estado)}
                        </div>
                        
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-gray-600">
                          <div>
                            <span className="font-medium">Inicio:</span> {formatDateTime(log.fecha_inicio)}
                          </div>
                          {log.fecha_fin && (
                            <div>
                              <span className="font-medium">Fin:</span> {formatDateTime(log.fecha_fin)}
                            </div>
                          )}
                          {log.tiempo_ejecucion_segundos && (
                            <div>
                              <span className="font-medium">Duración:</span> {formatDuration(log.tiempo_ejecucion_segundos)}
                            </div>
                          )}
                        </div>

                        {log.estado === 'success' && (
                          <div className="mt-2 grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                            <div className="text-green-600">
                              <span className="font-medium">Extraídos:</span> {log.eventos_extraidos}
                            </div>
                            <div className="text-blue-600">
                              <span className="font-medium">Nuevos:</span> {log.eventos_nuevos}
                            </div>
                            <div className="text-purple-600">
                              <span className="font-medium">Actualizados:</span> {log.eventos_actualizados}
                            </div>
                          </div>
                        )}

                        {log.estado === 'error' && log.detalles_error && (
                          <div className="mt-2 p-3 bg-red-50 border border-red-200 rounded text-sm text-red-700">
                            <span className="font-medium">Error:</span> {log.detalles_error}
                          </div>
                        )}

                        {log.mensaje && (
                          <div className="mt-2 text-sm text-gray-600">
                            <span className="font-medium">Mensaje:</span> {log.mensaje}
                          </div>
                        )}
                      </div>
                    </div>

                    <div className="flex items-center ml-4">
                      <button
                        onClick={() => setExpandedLog(expandedLog === log.id ? null : log.id)}
                        className="btn btn-outline btn-sm"
                      >
                        {expandedLog === log.id ? (
                          <>
                            <ChevronUpIcon className="h-4 w-4 mr-1" />
                            Menos
                          </>
                        ) : (
                          <>
                            <ChevronDownIcon className="h-4 w-4 mr-1" />
                            Detalles
                          </>
                        )}
                      </button>
                    </div>
                  </div>

                  {/* Detalles expandidos */}
                  {expandedLog === log.id && (
                    <div className="mt-4 pt-4 border-t border-gray-200 animate-slide-down">
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-sm">
                        <div>
                          <h4 className="font-medium text-gray-900 mb-2">Información del Log</h4>
                          <dl className="space-y-1">
                            <div className="flex justify-between">
                              <dt className="text-gray-500">ID:</dt>
                              <dd className="text-gray-900">{log.id}</dd>
                            </div>
                            <div className="flex justify-between">
                              <dt className="text-gray-500">Fuente ID:</dt>
                              <dd className="text-gray-900">{log.fuente_id}</dd>
                            </div>
                            <div className="flex justify-between">
                              <dt className="text-gray-500">Estado:</dt>
                              <dd>{getStatusBadge(log.estado)}</dd>
                            </div>
                            {log.tiempo_ejecucion_segundos && (
                              <div className="flex justify-between">
                                <dt className="text-gray-500">Tiempo total:</dt>
                                <dd className="text-gray-900">{log.tiempo_ejecucion_segundos}s</dd>
                              </div>
                            )}
                          </dl>
                        </div>

                        {log.estado === 'success' && (
                          <div>
                            <h4 className="font-medium text-gray-900 mb-2">Resultados</h4>
                            <dl className="space-y-1">
                              <div className="flex justify-between">
                                <dt className="text-gray-500">Total extraídos:</dt>
                                <dd className="text-gray-900">{log.eventos_extraidos}</dd>
                              </div>
                              <div className="flex justify-between">
                                <dt className="text-gray-500">Eventos nuevos:</dt>
                                <dd className="text-green-600 font-medium">{log.eventos_nuevos}</dd>
                              </div>
                              <div className="flex justify-between">
                                <dt className="text-gray-500">Eventos actualizados:</dt>
                                <dd className="text-blue-600 font-medium">{log.eventos_actualizados}</dd>
                              </div>
                            </dl>
                          </div>
                        )}
                      </div>

                      {log.detalles_error && (
                        <div className="mt-4">
                          <h4 className="font-medium text-red-800 mb-2">Detalles del Error</h4>
                          <div className="bg-red-50 border border-red-200 rounded p-3 text-sm text-red-700 font-mono">
                            {log.detalles_error}
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-12">
              <DocumentTextIcon className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900">No hay logs disponibles</h3>
              <p className="mt-1 text-sm text-gray-500">
                {selectedFuente 
                  ? 'No se encontraron logs para la fuente seleccionada.'
                  : 'No se han ejecutado procesos de scraping aún.'
                }
              </p>
            </div>
          )}
        </div>
      )}

      {/* Información adicional */}
      <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h3 className="text-sm font-medium text-blue-900 mb-2">
          ℹ️ Información sobre los logs
        </h3>
        <ul className="text-sm text-blue-800 space-y-1">
          <li>• Los logs se generan automáticamente cada vez que se ejecuta scraping</li>
          <li>• Los logs con estado "Exitoso" muestran cuántos eventos se extrajeron</li>
          <li>• Los logs con error incluyen detalles técnicos para debugging</li>
          <li>• Los logs se mantienen por tiempo limitado para optimizar el rendimiento</li>
        </ul>
      </div>
    </div>
  );
}