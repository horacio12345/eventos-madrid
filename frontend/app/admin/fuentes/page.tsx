// app/admin/fuentes/page.tsx

'use client';

import { useState } from 'react';
import { 
  PlusIcon,
  PencilIcon,
  TrashIcon,
  PlayIcon,
  PauseIcon,
  EyeIcon,
  GlobeAltIcon
} from '@heroicons/react/24/outline';
import { useFuentes, api } from '@/lib/api';
import { formatDateTime } from '@/lib/utils';
import type { FuenteWeb, CreateFuenteRequest, TestScrapingRequest } from '@/lib/types';
import LoadingSpinner from '@/components/LoadingSpinner';
import Alert from '@/components/Alert';
import Modal from '@/components/Modal';

export default function FuentesPage() {
  const { data: fuentes, loading, error, refetch } = useFuentes();
  const [selectedFuente, setSelectedFuente] = useState<FuenteWeb | null>(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showTestModal, setShowTestModal] = useState(false);
  const [testResult, setTestResult] = useState<any>(null);
  const [actionLoading, setActionLoading] = useState<number | null>(null);
  const [message, setMessage] = useState('');

  // Crear nueva fuente
  const [newFuente, setNewFuente] = useState<CreateFuenteRequest>({
    nombre: '',
    url: '',
    tipo: 'HTML',
    schema_extraccion: {},
    mapeo_campos: {},
    configuracion_scraping: {},
    frecuencia_actualizacion: '0 9 * * 1',
    activa: false
  });

  const handleCreateFuente = async () => {
    try {
      setActionLoading(-1);
      await api.admin.fuentes.create(newFuente);
      setMessage('Fuente creada exitosamente');
      setShowCreateModal(false);
      setNewFuente({
        nombre: '',
        url: '',
        tipo: 'HTML',
        schema_extraccion: {},
        mapeo_campos: {},
        configuracion_scraping: {},
        frecuencia_actualizacion: '0 9 * * 1',
        activa: false
      });
      refetch();
    } catch (error) {
      setMessage(`Error: ${error instanceof Error ? error.message : 'Error desconocido'}`);
    } finally {
      setActionLoading(null);
    }
  };

  const handleUpdateFuente = async () => {
    if (!selectedFuente) return;

    try {
      setActionLoading(selectedFuente.id);
      await api.admin.fuentes.update(selectedFuente.id, newFuente);
      setMessage('Fuente actualizada exitosamente');
      setShowCreateModal(false);
      setSelectedFuente(null);
      refetch();
    } catch (error) {
      setMessage(`Error: ${error instanceof Error ? error.message : 'Error desconocido'}`);
    } finally {
      setActionLoading(null);
    }
  };

  const handleFormSubmit = () => {
    if (selectedFuente) {
      handleUpdateFuente();
    } else {
      handleCreateFuente();
    }
  };

  const handleToggleActive = async (fuente: FuenteWeb) => {
    try {
      setActionLoading(fuente.id);
      await api.admin.fuentes.update(fuente.id, { activa: !fuente.activa });
      setMessage(`Fuente ${fuente.activa ? 'desactivada' : 'activada'} correctamente`);
      refetch();
    } catch (error) {
      setMessage(`Error: ${error instanceof Error ? error.message : 'Error desconocido'}`);
    } finally {
      setActionLoading(null);
    }
  };

  const handleDeleteFuente = async (fuente: FuenteWeb) => {
    if (!confirm(`¿Estás seguro de eliminar la fuente "${fuente.nombre}"?`)) return;
    
    try {
      setActionLoading(fuente.id);
      await api.admin.fuentes.delete(fuente.id);
      setMessage('Fuente eliminada correctamente');
      refetch();
    } catch (error) {
      setMessage(`Error: ${error instanceof Error ? error.message : 'Error desconocido'}`);
    } finally {
      setActionLoading(null);
    }
  };

  const handleTestFuente = async (fuente: FuenteWeb) => {
    try {
      setActionLoading(fuente.id);
      setSelectedFuente(fuente);
      
      const testConfig: TestScrapingRequest = {
        url: fuente.url,
        tipo: fuente.tipo,
        schema_extraccion: fuente.schema_extraccion,
        mapeo_campos: fuente.mapeo_campos,
        configuracion_scraping: fuente.configuracion_scraping
      };
      
      const result = await api.admin.fuentes.test(testConfig);
      setTestResult(result);
      setShowTestModal(true);
    } catch (error) {
      setMessage(`Error: ${error instanceof Error ? error.message : 'Error desconocido'}`);
    } finally {
      setActionLoading(null);
    }
  };

  return (
    <div className="container-wide">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Gestión de Fuentes</h1>
          <p className="text-gray-600">
            Configura y gestiona las fuentes web para el scraping automático
          </p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="btn btn-primary"
        >
          <PlusIcon className="h-5 w-5 mr-2" />
          Nueva Fuente
        </button>
      </div>

      {/* Mensaje de feedback */}
      {message && (
        <div className="mb-6">
          <Alert
            type={message.includes('Error') ? 'error' : 'success'}
            message={message}
            dismissible
            onDismiss={() => setMessage('')}
          />
        </div>
      )}

      {/* Lista de fuentes */}
      {loading ? (
        <div className="text-center py-12">
          <LoadingSpinner size="lg" text="Cargando fuentes..." />
        </div>
      ) : error ? (
        <Alert type="error" message={error} />
      ) : (
        <div className="bg-white shadow-card rounded-lg border border-gray-200">
          {fuentes && fuentes.length > 0 ? (
            <div className="divide-y divide-gray-200">
              {fuentes.map((fuente) => (
                <div key={fuente.id} className="p-6">
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="flex items-center">
                        <h3 className="text-lg font-medium text-gray-900 mr-3">
                          {fuente.nombre}
                        </h3>
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                          fuente.activa
                            ? 'bg-green-100 text-green-800'
                            : 'bg-gray-100 text-gray-800'
                        }`}>
                          {fuente.activa ? 'Activa' : 'Inactiva'}
                        </span>
                        <span className={`ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                          fuente.ultimo_estado === 'success'
                            ? 'bg-blue-100 text-blue-800'
                            : fuente.ultimo_estado === 'error'
                            ? 'bg-red-100 text-red-800'
                            : 'bg-gray-100 text-gray-800'
                        }`}>
                          {fuente.ultimo_estado === 'success' ? '✅ OK' : 
                           fuente.ultimo_estado === 'error' ? '❌ Error' : '⏳ Pendiente'}
                        </span>
                      </div>
                      
                      <div className="mt-2 text-sm text-gray-600 space-y-1">
                        <p><strong>URL:</strong> {fuente.url}</p>
                        <p><strong>Tipo:</strong> {fuente.tipo}</p>
                        <p><strong>Frecuencia:</strong> {fuente.frecuencia_actualizacion}</p>
                        {fuente.ultima_ejecucion && (
                          <p><strong>Última ejecución:</strong> {formatDateTime(fuente.ultima_ejecucion)}</p>
                        )}
                        {fuente.eventos_encontrados_ultima_ejecucion > 0 && (
                          <p><strong>Eventos encontrados:</strong> {fuente.eventos_encontrados_ultima_ejecucion}</p>
                        )}
                      </div>
                    </div>

                    <div className="flex items-center space-x-2 ml-4">
                      {/* Test */}
                      <button
                        onClick={() => handleTestFuente(fuente)}
                        disabled={actionLoading === fuente.id}
                        className="btn btn-outline btn-sm"
                        title="Probar fuente"
                      >
                        {actionLoading === fuente.id ? (
                          <LoadingSpinner size="sm" />
                        ) : (
                          <EyeIcon className="h-4 w-4" />
                        )}
                      </button>

                      {/* Activar/Desactivar */}
                      <button
                        onClick={() => handleToggleActive(fuente)}
                        disabled={actionLoading === fuente.id}
                        className={`btn btn-sm ${fuente.activa ? 'btn-secondary' : 'btn-primary'}`}
                        title={fuente.activa ? 'Desactivar' : 'Activar'}
                      >
                        {fuente.activa ? (
                          <PauseIcon className="h-4 w-4" />
                        ) : (
                          <PlayIcon className="h-4 w-4" />
                        )}
                      </button>

                      {/* Editar */}
                      <button
                        onClick={() => {
                          setSelectedFuente(fuente);
                          setNewFuente({
                            nombre: fuente.nombre,
                            url: fuente.url,
                            tipo: fuente.tipo,
                            schema_extraccion: fuente.schema_extraccion || {},
                            mapeo_campos: fuente.mapeo_campos || {},
                            configuracion_scraping: fuente.configuracion_scraping || {},
                            frecuencia_actualizacion: fuente.frecuencia_actualizacion,
                            activa: fuente.activa
                          });
                          setShowCreateModal(true);
                          console.log('Editando fuente:', fuente.id, fuente.nombre);
                        }}
                        className="btn btn-outline btn-sm"
                        title="Editar fuente"
                      >
                        <PencilIcon className="h-4 w-4" />
                      </button>

                      {/* Eliminar */}
                      <button
                        onClick={() => handleDeleteFuente(fuente)}
                        disabled={actionLoading === fuente.id}
                        className="btn btn-danger btn-sm"
                        title="Eliminar fuente"
                      >
                        <TrashIcon className="h-4 w-4" />
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-12">
              <h3 className="mt-2 text-sm font-medium text-gray-900">No hay fuentes configuradas</h3>
              <p className="mt-1 text-sm text-gray-500">
                Comienza agregando una nueva fuente web para scraping.
              </p>
              <div className="mt-6">
                <button
                  onClick={() => setShowCreateModal(true)}
                  className="btn btn-primary"
                >
                  <PlusIcon className="h-5 w-5 mr-2" />
                  Crear primera fuente
                </button>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Modal crear fuente */}
      <Modal
        isOpen={showCreateModal}
        onClose={() => {
          setShowCreateModal(false);
          setSelectedFuente(null);
          setNewFuente({
            nombre: '',
            url: '',
            tipo: 'HTML',
            schema_extraccion: {},
            mapeo_campos: {},
            configuracion_scraping: {},
            frecuencia_actualizacion: '0 9 * * 1',
            activa: false
          });
        }}
        title={selectedFuente ? `Editar ${selectedFuente.nombre}` : "Crear Nueva Fuente"}
        size="lg"
      >
        <div className="space-y-4">
          <div>
            <label className="label">Nombre</label>
            <input
              type="text"
              value={newFuente.nombre}
              onChange={(e) => setNewFuente({...newFuente, nombre: e.target.value})}
              className="input"
              placeholder="Ej: Ayuntamiento de Madrid"
            />
          </div>

          <div>
            <label className="label">URL</label>
            <input
              type="url"
              value={newFuente.url}
              onChange={(e) => setNewFuente({...newFuente, url: e.target.value})}
              className="input"
              placeholder="https://..."
            />
          </div>

          <div>
            <label className="label">Tipo</label>
            <select
              value={newFuente.tipo}
              onChange={(e) => setNewFuente({...newFuente, tipo: e.target.value as any})}
              className="select"
            >
              <option value="HTML">HTML</option>
              <option value="PDF">PDF</option>
              <option value="IMAGE">Imagen</option>
            </select>
          </div>

          <div>
            <label className="label">Frecuencia (cron)</label>
            <input
              type="text"
              value={newFuente.frecuencia_actualizacion}
              onChange={(e) => setNewFuente({...newFuente, frecuencia_actualizacion: e.target.value})}
              className="input"
              placeholder="0 9 * * 1"
            />
            <p className="text-xs text-gray-500 mt-1">
              Formato cron: minuto hora día mes día_semana (Ej: 0 9 * * 1 = Lunes 9:00)
            </p>
          </div>

          <div className="flex items-center">
            <input
              type="checkbox"
              id="activa"
              checked={newFuente.activa}
              onChange={(e) => setNewFuente({...newFuente, activa: e.target.checked})}
              className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
            />
            <label htmlFor="activa" className="ml-2 block text-sm text-gray-900">
              Activar fuente inmediatamente
            </label>
          </div>

          <div className="flex justify-end space-x-3 pt-4">
            <button
              onClick={() => setShowCreateModal(false)}
              className="btn btn-secondary"
            >
              Cancelar
            </button>
            <button
              type='button'
              onClick={(e) => {
                  e.preventDefault();
                  e.stopPropagation();
                  console.log('🔥 BUTTON CLICKED!');
                  handleFormSubmit();
                }}
                className="btn btn-primary"
              >
              {actionLoading === -1 ? <LoadingSpinner size="sm" /> : 
              selectedFuente ? 'Actualizar Fuente' : 'Crear Fuente'}
            </button>
          </div>
        </div>
      </Modal>

      {/* Modal test resultado */}
      <Modal
        isOpen={showTestModal}
        onClose={() => setShowTestModal(false)}
        title={`Test de ${selectedFuente?.nombre}`}
        size="xl"
      >
        {testResult && (
          <div className="space-y-4">
            <div className={`p-4 rounded-lg ${
              testResult.estado === 'success' 
                ? 'bg-green-50 border border-green-200' 
                : 'bg-red-50 border border-red-200'
            }`}>
              <h4 className={`font-medium ${
                testResult.estado === 'success' ? 'text-green-800' : 'text-red-800'
              }`}>
                {testResult.estado === 'success' ? '✅ Test exitoso' : '❌ Test fallido'}
              </h4>
              <p className={`text-sm mt-1 ${
                testResult.estado === 'success' ? 'text-green-700' : 'text-red-700'
              }`}>
                {testResult.estado === 'success' 
                  ? `Se encontraron ${testResult.eventos_encontrados} eventos`
                  : testResult.error
                }
              </p>
            </div>

            {testResult.preview_eventos && testResult.preview_eventos.length > 0 && (
              <div>
                <h4 className="font-medium text-gray-900 mb-2">Preview de eventos:</h4>
                <div className="space-y-3 max-h-60 overflow-y-auto">
                  {testResult.preview_eventos.map((evento: any, index: number) => (
                    <div key={index} className="bg-gray-50 p-3 rounded border">
                      <p className="font-medium text-sm">{evento.titulo}</p>
                      <p className="text-xs text-gray-600">{evento.fecha_inicio}</p>
                      <p className="text-xs text-gray-600">{evento.precio}</p>
                      {evento.ubicacion && <p className="text-xs text-gray-600">{evento.ubicacion}</p>}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {testResult.errores && testResult.errores.length > 0 && (
              <div>
                <h4 className="font-medium text-red-800 mb-2">Errores:</h4>
                <ul className="text-sm text-red-700 space-y-1">
                  {testResult.errores.map((error: string, index: number) => (
                    <li key={index}>• {error}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
      </Modal>
    </div>
  );
}