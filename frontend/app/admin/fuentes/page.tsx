// app/admin/fuentes/page.tsx

'use client';

import { useState, useEffect } from 'react';
import { 
  PlusIcon,
  PencilIcon,
  TrashIcon,
  PlayIcon,
  PauseIcon,
  DocumentArrowUpIcon,
  CheckCircleIcon,
  XMarkIcon,
  FolderOpenIcon
} from '@heroicons/react/24/outline';
import { formatDateTime } from '@/lib/utils';
import LoadingSpinner from '@/components/LoadingSpinner';
import Alert from '@/components/Alert';
import Modal from '@/components/Modal';
import { useFuentes, api } from '@/lib/api';
import FileUpload from '@/components/FileUpload';

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
  const [showFilesModal, setShowFilesModal] = useState(false);
  const [actionLoading, setActionLoading] = useState<number | null>(null);
  const [message, setMessage] = useState('');

  // Estado para el modal de gestión de archivos
  const [filesState, setFilesState] = useState<{
    files: string[];
    loading: boolean;
    error: string | null;
  }>({
    files: [],
    loading: false,
    error: null,
  });

  // Estado para upload y procesamiento
  const [uploadState, setUploadState] = useState<{
    file: File | null;
    uploadedFilePath: string | null;
    uploading: boolean;
    processing: boolean;
    events: any[];
    error: string;
    step: 'upload' | 'uploaded' | 'preview' | 'completed';
  }>({
    file: null,
    uploadedFilePath: null,
    uploading: false,
    processing: false,
    events: [],
    error: '',
    step: 'upload'
  });

  const [newAgente, setNewAgente] = useState<CreateAgenteRequest>({
    nombre: '',
    activa: false
  });

  const handleCreateAgente = async () => {
    try {
      setActionLoading(-1);
      const agenteData = {
        nombre: newAgente.nombre,
        url: 'manual-upload',
        tipo: 'AGENTE',
        activa: newAgente.activa,
        frecuencia_actualizacion: '0 9 * * 1'
      };
      await api.admin.fuentes.create(agenteData);
      setMessage('Agente creado exitosamente');
      setShowCreateModal(false);
      setNewAgente({ nombre: '', activa: false });
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
      const agenteData = { nombre: newAgente.nombre, activa: newAgente.activa };
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
    if (selectedAgente) handleUpdateAgente();
    else handleCreateAgente();
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

  const handleOpenUploadModal = (agente: FuenteWeb) => {
    setSelectedAgente(agente);
    setShowUploadModal(true);
    setUploadState({
      file: null, uploadedFilePath: null, uploading: false, processing: false,
      events: [], error: '', step: 'upload'
    });
  };

  const handleFileUpload = async (file: File) => {
    if (!selectedAgente) return;
    setUploadState(prev => ({ ...prev, file, uploading: true, error: '' }));
    try {
      const result = await api.admin.uploadFile(file, selectedAgente.nombre);
      setUploadState(prev => ({ ...prev, uploading: false, uploadedFilePath: result.file_path, step: 'uploaded' }));
    } catch (error) {
      setUploadState(prev => ({ ...prev, uploading: false, error: error instanceof Error ? error.message : 'Error subiendo archivo' }));
    }
  };

  const handleProcessFile = async () => {
    if (!uploadState.uploadedFilePath) return;
    setUploadState(prev => ({ ...prev, processing: true, error: '' }));
    try {
      const result = await api.admin.extractEvents('ssreyes', { pdf_url: uploadState.uploadedFilePath });
      if (result.estado === 'error') throw new Error(result.error || 'El backend devolvió un error');
      setUploadState(prev => ({ ...prev, processing: false, events: result.eventos || [], step: 'preview' }));
    } catch (error) {
      setUploadState(prev => ({ ...prev, processing: false, error: error instanceof Error ? error.message : 'Error procesando archivo' }));
    }
  };

  const handleConfirmEvents = async () => {
    try {
      setUploadState(prev => ({ ...prev, processing: true }));
      setMessage(`${uploadState.events.length} eventos procesados exitosamente`);
      setUploadState(prev => ({ ...prev, step: 'completed', processing: false }));
      refetch();
      setTimeout(() => setShowUploadModal(false), 2000);
    } catch (error) {
      setUploadState(prev => ({ ...prev, processing: false, error: error instanceof Error ? error.message : 'Error guardando eventos' }));
    }
  };

  const handleCloseUploadModal = () => {
    setShowUploadModal(false);
  };

  const handleOpenFilesModal = async (agente: FuenteWeb) => {
    setSelectedAgente(agente);
    setShowFilesModal(true);
    setFilesState({ files: [], loading: true, error: null });
    try {
      const files = await api.admin.uploads.getForAgent(agente.nombre);
      setFilesState({ files, loading: false, error: null });
    } catch (error) {
      setFilesState({ files: [], loading: false, error: error instanceof Error ? error.message : 'Error cargando archivos' });
    }
  };

  const handleDeleteFile = async (filename: string) => {
    if (!confirm(`¿Seguro que quieres borrar "${filename}" y sus eventos asociados? Esta acción es irreversible.`)) return;
    try {
      setFilesState(prev => ({ ...prev, loading: true }));
      const result = await api.admin.uploads.deleteFile(filename);
      setMessage(result.message);
      // Refrescar la lista de archivos
      if (selectedAgente) {
        const files = await api.admin.uploads.getForAgent(selectedAgente.nombre);
        setFilesState({ files, loading: false, error: null });
      }
      refetch(); // Refrescar datos de agentes por si cambia el número de eventos
    } catch (error) {
      setFilesState(prev => ({ ...prev, loading: false, error: error instanceof Error ? error.message : 'Error borrando archivo' }));
    }
  };

  return (
    <div className="container-wide">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Gestión de Agentes</h1>
          <p className="text-gray-600">Crea y gestiona agentes para procesar archivos de diferentes fuentes.</p>
        </div>
        <button onClick={() => { setSelectedAgente(null); setNewAgente({ nombre: '', activa: false }); setShowCreateModal(true); }} className="btn btn-primary">
          <PlusIcon className="h-5 w-5 mr-2" /> Nuevo Agente
        </button>
      </div>

      {message && <div className="mb-6"><Alert type={message.includes('Error') ? 'error' : 'success'} message={message} dismissible onDismiss={() => setMessage('')} /></div>}

      {loading ? <div className="text-center py-12"><LoadingSpinner size="lg" text="Cargando agentes..." /></div>
        : error ? <Alert type="error" message={error} />
        : <div className="bg-white shadow-card rounded-lg border border-gray-200">
            {agentes && agentes.length > 0 ? (
              <div className="divide-y divide-gray-200">
                {agentes.map((agente) => (
                  <div key={agente.id} className="p-6">
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <h3 className="text-lg font-medium text-gray-900">{agente.nombre}</h3>
                        <div className="mt-2 text-sm text-gray-600 space-y-1">
                          {agente.ultima_ejecucion && <p><strong>Último procesamiento:</strong> {formatDateTime(agente.ultima_ejecucion)}</p>}
                          {(agente.eventos_encontrados_ultima_ejecucion || 0) > 0 && <p><strong>Eventos procesados:</strong> {agente.eventos_encontrados_ultima_ejecucion}</p>}
                        </div>
                      </div>
                      <div className="flex items-center space-x-2 ml-4">
                        <button onClick={() => handleOpenUploadModal(agente)} className="btn btn-primary btn-sm" title="Subir archivo"><DocumentArrowUpIcon className="h-4 w-4" /></button>
                        <button onClick={() => handleOpenFilesModal(agente)} className="btn btn-secondary btn-sm" title="Gestionar archivos subidos"><FolderOpenIcon className="h-4 w-4" /></button>
                        <button onClick={() => { setSelectedAgente(agente); setNewAgente({ nombre: agente.nombre, activa: agente.activa }); setShowCreateModal(true); }} className="btn btn-outline btn-sm" title="Editar agente"><PencilIcon className="h-4 w-4" /></button>
                        <button onClick={() => handleDeleteAgente(agente)} disabled={actionLoading === agente.id} className="btn btn-danger btn-sm" title="Eliminar agente"><TrashIcon className="h-4 w-4" /></button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-12">
                <h3 className="mt-2 text-sm font-medium text-gray-900">No hay agentes configurados</h3>
                <p className="mt-1 text-sm text-gray-500">Crea un agente para empezar a procesar archivos.</p>
                <div className="mt-6"><button onClick={() => setShowCreateModal(true)} className="btn btn-primary"><PlusIcon className="h-5 w-5 mr-2" />Crear primer agente</button></div>
              </div>
            )}
          </div>
      }

      <Modal isOpen={showCreateModal} onClose={() => setShowCreateModal(false)} title={selectedAgente ? `Editar ${selectedAgente.nombre}` : "Crear Nuevo Agente"} size="md">
        <div className="space-y-4">
          <div>
            <label className="label">Nombre del Agente</label>
            <input type="text" value={newAgente.nombre} onChange={(e) => setNewAgente({...newAgente, nombre: e.target.value})} className="input" placeholder="Ej: Agente San Sebastián de los Reyes" />
          </div>
          <div className="flex justify-end space-x-3 pt-4">
            <button onClick={() => setShowCreateModal(false)} className="btn btn-secondary">Cancelar</button>
            <button type='button' onClick={handleFormSubmit} disabled={!newAgente.nombre.trim()} className="btn btn-primary">{actionLoading === -1 ? <LoadingSpinner size="sm" /> : selectedAgente ? 'Actualizar Agente' : 'Crear Agente'}</button>
          </div>
        </div>
      </Modal>

      <Modal isOpen={showUploadModal} onClose={handleCloseUploadModal} title={`Procesar Archivo - ${selectedAgente?.nombre}`} size="lg">
        <div className="space-y-6">
          {uploadState.step === 'upload' && (
            <div>
              <FileUpload onFileUpload={handleFileUpload} acceptedTypes={['.pdf']} maxSizeMB={10} />
              {uploadState.uploading && <div className="mt-4 text-center"><LoadingSpinner size="lg" text="Subiendo archivo..." /></div>}
            </div>
          )}
          {uploadState.step === 'uploaded' && (
            <div className="text-center py-8">
              <CheckCircleIcon className="mx-auto h-16 w-16 text-green-500 mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">¡Archivo Subido!</h3>
              <p className="text-gray-600 mb-6">El archivo <strong>{uploadState.file?.name}</strong> está listo para ser procesado.</p>
              <button onClick={handleProcessFile} disabled={uploadState.processing} className="btn btn-primary">{uploadState.processing ? <LoadingSpinner size="sm" /> : 'Procesar Archivo'}</button>
            </div>
          )}
          {uploadState.step === 'preview' && (
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">Eventos Encontrados: {uploadState.events.length}</h3>
              <div className="max-h-96 overflow-y-auto space-y-3 p-1">
                {uploadState.events.map((event, index) => (
                  <div key={index} className="p-3 border rounded-lg"><h4 className="font-medium text-gray-900">{event.titulo}</h4><p className="text-sm text-gray-600 mt-1">📅 {event.fecha_inicio} | 💰 {event.precio}</p></div>
                ))}
              </div>
              <div className="flex justify-end space-x-3 pt-4">
                <button onClick={handleCloseUploadModal} className="btn btn-secondary">Cancelar</button>
                <button onClick={handleConfirmEvents} disabled={uploadState.processing} className="btn btn-primary">{uploadState.processing ? <LoadingSpinner size="sm" /> : <><CheckCircleIcon className="h-4 w-4 mr-2" />Guardar {uploadState.events.length} Eventos</>}</button>
              </div>
            </div>
          )}
          {uploadState.step === 'completed' && <div className="text-center py-8"><CheckCircleIcon className="mx-auto h-16 w-16 text-green-500 mb-4" /><h3 className="text-lg font-medium">¡Procesamiento Completado!</h3></div>}
          {uploadState.error && <Alert type="error" message={uploadState.error} dismissible onDismiss={() => setUploadState(prev => ({ ...prev, error: '' }))} />}
        </div>
      </Modal>

      <Modal isOpen={showFilesModal} onClose={() => setShowFilesModal(false)} title={`Archivos Subidos - ${selectedAgente?.nombre}`} size="xl">
        {filesState.loading && <div className="text-center"><LoadingSpinner text="Cargando archivos..." /></div>}
        {filesState.error && <Alert type="error" message={filesState.error} />}
        {!filesState.loading && !filesState.error && (
          <div className="space-y-3 max-h-96 overflow-y-auto">
            {filesState.files.length > 0 ? filesState.files.map(file => (
              <div key={file} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <span className="text-sm font-mono text-gray-700">{file}</span>
                <button onClick={() => handleDeleteFile(file)} className="btn btn-danger btn-sm"><TrashIcon className="h-4 w-4" /></button>
              </div>
            )) : <p className="text-center text-gray-500 py-4">No hay archivos subidos para este agente.</p>}
          </div>
        )}
      </Modal>
    </div>
  );
}