// app/admin/fuentes/page.tsx

'use client';

import { useState } from 'react';
import { 
  PlusIcon,
  PencilIcon,
  TrashIcon,
  PlayIcon,
  PauseIcon,
  DocumentArrowUpIcon
} from '@heroicons/react/24/outline';
import { formatDateTime } from '@/lib/utils';
import LoadingSpinner from '@/components/LoadingSpinner';
import Alert from '@/components/Alert';
import Modal from '@/components/Modal';
import { useFuentes, api } from '@/lib/api';

interface FuenteWeb {
  id: number;
  nombre: string;
  activa: boolean;
  ultima_ejecucion?: string;
  ultimo_estado?: string;
  eventos_encontrados_ultima_ejecucion?: number;
}

interface CreateAgenteRequest {
  nombre: string;
  activa: boolean;
}

export default function AgentesPage() {
  const { data: agentes, loading, error, refetch } = useFuentes();
  const [selectedAgente, setSelectedAgente] = useState<FuenteWeb | null>(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [actionLoading, setActionLoading] = useState<number | null>(null);
  const [message, setMessage] = useState('');

  // Crear nuevo agente - SIN TIPO PREDEFINIDO
  const [newAgente, setNewAgente] = useState<CreateAgenteRequest>({
    nombre: '',
    activa: false
  });

  const handleCreateAgente = async () => {
    try {
      setActionLoading(-1);
      const agenteData = {
        nombre: newAgente.nombre,
        url: 'manual-upload', // Sin prefijo de tipo
        tipo: 'AGENTE',
        activa: newAgente.activa,
        frecuencia_actualizacion: '0 9 * * 1'
      };
      
      await api.admin.fuentes.create(agenteData);
      setMessage('Agente creado exitosamente');
      setShowCreateModal(false);
      setNewAgente({
        nombre: '',
        activa: false
      });
      refetch();
    } catch (error) {
      setMessage(`Error: ${error instanceof Error ? error.message : 'Error desconocido'}`);
    } finally {
      setActionLoading(-1);
    }
  };

  const handleUpdateAgente = async () => {
    if (!selectedAgente) return;

    try {
      setActionLoading(selectedAgente.id);
      const agenteData = {
        nombre: newAgente.nombre,
        activa: newAgente.activa
      };
      
      await api.admin.fuentes.update(selectedAgente.id, agenteData);
      setMessage('Agente actualizado exitosamente');
      setShowCreateModal(false);
      setSelectedAgente(null);
      refetch();
    } catch (error) {
      setMessage(`Error: ${error instanceof Error ? error.message : 'Error desconocido'}`);
    } finally {
      setActionLoading(null);
    }
  };

  const handleFormSubmit = () => {
    if (selectedAgente) {
      handleUpdateAgente();
    } else {
      handleCreateAgente();
    }
  };

  const handleToggleActive = async (agente: FuenteWeb) => {
    try {
      setActionLoading(agente.id);
      await api.admin.fuentes.update(agente.id, { activa: !agente.activa });
      setMessage(`Agente ${agente.activa ? 'desactivado' : 'activado'} correctamente`);
      refetch();
    } catch (error) {
      setMessage(`Error: ${error instanceof Error ? error.message : 'Error desconocido'}`);
    } finally {
      setActionLoading(null);
    }
  };

  const handleDeleteAgente = async (agente: FuenteWeb) => {
    if (!confirm(`¿Estás seguro de eliminar el agente "${agente.nombre}"?`)) return;
    
    try {
      setActionLoading(agente.id);
      await api.admin.fuentes.delete(agente.id);
      setMessage('Agente eliminado correctamente');
      refetch();
    } catch (error) {
      setMessage(`Error: ${error instanceof Error ? error.message : 'Error desconocido'}`);
    } finally {
      setActionLoading(null);
    }
  };

  const handleUploadAndProcess = async (agente: FuenteWeb) => {
    setSelectedAgente(agente);
    setShowUploadModal(true);
  };

  return (
    <div className="container-wide">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Gestión de Agentes</h1>
          <p className="text-gray-600">
            Crea agentes para procesar archivos de diferentes fuentes
          </p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="btn btn-primary"
        >
          <PlusIcon className="h-5 w-5 mr-2" />
          Nuevo Agente
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

      {/* Lista de agentes */}
      {loading ? (
        <div className="text-center py-12">
          <LoadingSpinner size="lg" text="Cargando agentes..." />
        </div>
      ) : error ? (
        <Alert type="error" message={error} />
      ) : (
        <div className="bg-white shadow-card rounded-lg border border-gray-200">
          {agentes && agentes.length > 0 ? (
            <div className="divide-y divide-gray-200">
              {agentes.map((agente) => (
                <div key={agente.id} className="p-6">
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="flex items-center">
                        <h3 className="text-lg font-medium text-gray-900 mr-3">
                          {agente.nombre}
                        </h3>
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                          agente.activa
                            ? 'bg-green-100 text-green-800'
                            : 'bg-gray-100 text-gray-800'
                        }`}>
                          {agente.activa ? 'Activo' : 'Inactivo'}
                        </span>
                      </div>
                      
                      <div className="mt-2 text-sm text-gray-600 space-y-1">
                        {agente.ultima_ejecucion && (
                          <p><strong>Último procesamiento:</strong> {formatDateTime(agente.ultima_ejecucion)}</p>
                        )}
                        {(agente.eventos_encontrados_ultima_ejecucion || 0) > 0 && (
                          <p><strong>Eventos procesados:</strong> {agente.eventos_encontrados_ultima_ejecucion}</p>
                        )}
                      </div>
                    </div>

                    <div className="flex items-center space-x-2 ml-4">
                      {/* Upload y Procesar */}
                      <button
                        onClick={() => handleUploadAndProcess(agente)}
                        disabled={actionLoading === agente.id}
                        className="btn btn-primary btn-sm"
                        title="Subir archivo y procesar"
                      >
                        <DocumentArrowUpIcon className="h-4 w-4" />
                      </button>

                      {/* Activar/Desactivar */}
                      <button
                        onClick={() => handleToggleActive(agente)}
                        disabled={actionLoading === agente.id}
                        className={`btn btn-sm ${agente.activa ? 'btn-secondary' : 'btn-success'}`}
                        title={agente.activa ? 'Desactivar' : 'Activar'}
                      >
                        {agente.activa ? (
                          <PauseIcon className="h-4 w-4" />
                        ) : (
                          <PlayIcon className="h-4 w-4" />
                        )}
                      </button>

                      {/* Editar */}
                      <button
                        onClick={() => {
                          setSelectedAgente(agente);
                          setNewAgente({
                            nombre: agente.nombre,
                            activa: agente.activa
                          });
                          setShowCreateModal(true);
                        }}
                        className="btn btn-outline btn-sm"
                        title="Editar agente"
                      >
                        <PencilIcon className="h-4 w-4" />
                      </button>

                      {/* Eliminar */}
                      <button
                        onClick={() => handleDeleteAgente(agente)}
                        disabled={actionLoading === agente.id}
                        className="btn btn-danger btn-sm"
                        title="Eliminar agente"
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
              <h3 className="mt-2 text-sm font-medium text-gray-900">No hay agentes configurados</h3>
              <p className="mt-1 text-sm text-gray-500">
                Crea agentes para procesar archivos de cualquier fuente.
              </p>
              <div className="mt-6">
                <button
                  onClick={() => setShowCreateModal(true)}
                  className="btn btn-primary"
                >
                  <PlusIcon className="h-5 w-5 mr-2" />
                  Crear primer agente
                </button>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Modal crear/editar agente - SIMPLIFICADO */}
      <Modal
        isOpen={showCreateModal}
        onClose={() => {
          setShowCreateModal(false);
          setSelectedAgente(null);
          setNewAgente({
            nombre: '',
            activa: false
          });
        }}
        title={selectedAgente ? `Editar ${selectedAgente.nombre}` : "Crear Nuevo Agente"}
        size="md"
      >
        <div className="space-y-4">
          <div>
            <label className="label">Nombre del Agente</label>
            <input
              type="text"
              value={newAgente.nombre}
              onChange={(e) => setNewAgente({...newAgente, nombre: e.target.value})}
              className="input"
              placeholder="Ej: Agente San Sebastián de los Reyes"
            />
            <p className="text-xs text-gray-500 mt-1">
              Nombre libre para identificar este agente
            </p>
          </div>

          <div className="flex items-center">
            <input
              type="checkbox"
              id="activa"
              checked={newAgente.activa}
              onChange={(e) => setNewAgente({...newAgente, activa: e.target.checked})}
              className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
            />
            <label htmlFor="activa" className="ml-2 block text-sm text-gray-900">
              Activar agente inmediatamente
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
              onClick={handleFormSubmit}
              disabled={!newAgente.nombre.trim()}
              className="btn btn-primary"
            >
              {actionLoading === -1 ? <LoadingSpinner size="sm" /> : 
              selectedAgente ? 'Actualizar Agente' : 'Crear Agente'}
            </button>
          </div>
        </div>
      </Modal>

      {/* Modal upload - placeholder */}
      <Modal
        isOpen={showUploadModal}
        onClose={() => setShowUploadModal(false)}
        title={`Subir Archivo - ${selectedAgente?.nombre}`}
        size="lg"
      >
        <div className="text-center py-8">
          <DocumentArrowUpIcon className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">Upload en desarrollo</h3>
          <p className="mt-1 text-sm text-gray-500">
            Aquí podrás subir archivos y el sistema detectará automáticamente qué estrategia usar.
          </p>
        </div>
      </Modal>
    </div>
  );
}