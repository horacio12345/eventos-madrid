// app/admin/dashboard/page.tsx

'use client';

import { useState } from 'react';
import Link from 'next/link';
import { 
  CalendarIcon,
  GlobeAltIcon,
  CheckCircleIcon,
  PlayIcon,
  ChartBarIcon,
  DocumentArrowUpIcon
} from '@heroicons/react/24/outline';
import { useEventos, useFuentes } from '@/lib/api';
import { getCategoriaConfig } from '@/lib/utils';
import LoadingSpinner from '@/components/LoadingSpinner';
import Alert from '@/components/Alert';

export default function DashboardPage() {
  const [processingFiles, setProcessingFiles] = useState(false);
  const [updateMessage, setUpdateMessage] = useState('');

  // Cargar datos
  const { data: eventos, loading: eventosLoading, refetch: refetchEventos } = useEventos();
  const { data: fuentes, loading: fuentesLoading, refetch: refetchFuentes } = useFuentes();

  // Categorías con eventos
  const eventosPorCategoria = eventos?.reduce((acc, evento) => {
    const categoria = evento.categoria;
    acc[categoria] = (acc[categoria] || 0) + 1;
    return acc;
  }, {} as Record<string, number>) || {};

  // Trigger procesamiento manual de archivos
  const handleTriggerProcessing = async () => {
    setProcessingFiles(true);
    setUpdateMessage('');
    
    try {
      // Por ahora redirigir a gestión de fuentes
      setUpdateMessage('Ir a "Gestión de Fuentes" para procesar archivos');
      
      // Refrescar datos después de 2 segundos
      setTimeout(() => {
        refetchEventos();
        refetchFuentes();
      }, 2000);
      
    } catch (error) {
      setUpdateMessage(`Error: ${error instanceof Error ? error.message : 'Error desconocido'}`);
    } finally {
      setProcessingFiles(false);
    }
  };

  return (
    <div className="container-wide">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-xl font-bold text-gray-900 mb-2">Dashboard</h1>
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
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
        {/* Total Eventos */}
        <div className="bg-white rounded-lg shadow-card p-6 border border-gray-100">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <CalendarIcon className="h-8 w-8 text-primary-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Total Eventos</p>
              <p className="text-2xl font-bold text-gray-900">
                {eventosLoading ? <LoadingSpinner size="sm" /> : (eventos?.length || 0)}
              </p>
            </div>
          </div>
        </div>

        {/* Total Agentes */}
        <div className="bg-white rounded-lg shadow-card p-6 border border-gray-100">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <GlobeAltIcon className="h-8 w-8 text-blue-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Total Agentes</p>
              <p className="text-2xl font-bold text-gray-900">
                {fuentesLoading ? <LoadingSpinner size="sm" /> : (fuentes?.length || 0)}
              </p>
            </div>
          </div>
        </div>

        {/* Agentes Activos */}
        <div className="bg-white rounded-lg shadow-card p-6 border border-gray-100">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <PlayIcon className="h-8 w-8 text-purple-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Agentes Activos</p>
              <p className="text-2xl font-bold text-gray-900">
                {fuentesLoading ? <LoadingSpinner size="sm" /> : (fuentes?.filter(f => f.activa).length || 0)}
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
              onClick={handleTriggerProcessing}
              disabled={processingFiles}
              className="w-full btn btn-primary btn-sm justify-start"
            >
              {processingFiles ? (
                <LoadingSpinner size="sm" />
              ) : (
                <DocumentArrowUpIcon className="h-5 w-5" />
              )}
              <span className="ml-2">
                {processingFiles ? 'Procesando archivos...' : 'Procesar Archivos'}
              </span>
            </button>

            <Link href="/admin/fuentes" className="w-full btn btn-primary btn-sm justify-start">
              <GlobeAltIcon className="h-5 w-5" />
              <span className="ml-2">Gestionar Agentes</span>
            </Link>

            <Link href="/admin/logs" className="w-full btn btn-primary btn-sm justify-start">
              <ChartBarIcon className="h-5 w-5" />
              <span className="ml-2">Ver Historial del Sistema</span>
            </Link>
          </div>
        </div>

        {/* Estado del sistema */}
        <div className="bg-white rounded-lg shadow-card p-6 border border-gray-100">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Estado del Sistema</h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-500">Eventos en base de datos:</span>
              <span className="text-sm font-medium text-gray-900">
                {eventos?.length || 0}
              </span>
            </div>
            
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-500">Agentes configurados:</span>
              <span className="text-sm font-medium text-blue-600">
                {fuentes?.length || 0}
              </span>
            </div>
            
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-500">Sistema:</span>
              <span className="text-sm font-medium text-green-600">
                Operativo
              </span>
            </div>
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

        {/* Estado de agentes */}
        <div className="bg-white rounded-lg shadow-card p-6 border border-gray-100">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Estado de Agentes</h3>
          {fuentesLoading ? (
            <LoadingSpinner size="sm" />
          ) : (
            <div className="space-y-3">
              {fuentes?.slice(0, 5).map(fuente => (
                <div key={fuente.id} className="flex items-center justify-between">
                  <div className="flex items-center">
                    <div className={`w-3 h-3 rounded-full mr-3 ${
                      fuente.activa 
                        ? fuente.ultimo_estado === 'success' ? 'bg-green-500' : 'bg-gray-500'
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
                  No hay agentes configurados
                </p>
              )}
              {fuentes && fuentes.length > 5 && (
                <Link 
                  href="/admin/fuentes" 
                  className="block text-sm text-primary-600 hover:text-primary-800 text-center pt-2"
                >
                  Ver todos los agentes →
                </Link>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}