// app/page.tsx

'use client';

import { useState, useEffect } from 'react';
import { MagnifyingGlassIcon, FunnelIcon, CalendarIcon, MapPinIcon } from '@heroicons/react/24/outline';
import { useEventos, useCategorias } from '@/lib/api';
import { 
  getAllCategorias, 
  getCategoriaConfig, 
  formatDateLong, 
  getRelativeDate, 
  formatPrice,
  filterEventos,
  debounce
} from '@/lib/utils';
import type { Evento, EventoCategoria, EventoFilter } from '@/lib/types';
import EventCard from '@/components/EventCard';
import LoadingSpinner from '@/components/LoadingSpinner';

export default function HomePage() {
  // Estado para filtros
  const [filters, setFilters] = useState<EventoFilter>({});
  const [searchTerm, setSearchTerm] = useState('');
  const [showFilters, setShowFilters] = useState(false);

  // Datos de la API
  const { data: eventos, loading: eventosLoading, error: eventosError, refetch } = useEventos();
  const { data: categorias } = useCategorias();

  // Eventos filtrados
  const [filteredEventos, setFilteredEventos] = useState<Evento[]>([]);

  // Debounced search
  const debouncedSearch = debounce((term: string) => {
    setFilters(prev => ({ ...prev, busqueda: term }));
  }, 300);

  // Efecto para filtrar eventos
  useEffect(() => {
    if (eventos) {
      const filtered = filterEventos(eventos, filters);
      setFilteredEventos(filtered);
    }
  }, [eventos, filters]);

  // Efecto para búsqueda
  useEffect(() => {
    debouncedSearch(searchTerm);
  }, [searchTerm, debouncedSearch]);

  const handleCategoryFilter = (categoria: EventoCategoria | undefined) => {
    setFilters(prev => ({ ...prev, categoria }));
  };

  const clearFilters = () => {
    setFilters({});
    setSearchTerm('');
  };

  const activeFiltersCount = Object.values(filters).filter(Boolean).length;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="container-wide">
          <div className="py-6">
            <div className="text-center">
              <h1 className="text-4xl font-bold text-gray-900 mb-2">
                🎭 Eventos Mayores Madrid
              </h1>
              <p className="text-xl text-gray-600 max-w-3xl mx-auto">
                Descubre actividades gratuitas y de bajo coste especialmente seleccionadas 
                para personas mayores en la Comunidad de Madrid
              </p>
            </div>
          </div>
        </div>
      </header>

      {/* Barra de búsqueda y filtros */}
      <section className="bg-white border-b border-gray-200 sticky top-0 z-40">
        <div className="container-wide">
          <div className="py-4">
            <div className="flex flex-col lg:flex-row gap-4 items-center">
              {/* Búsqueda */}
              <div className="relative flex-1 max-w-md">
                <MagnifyingGlassIcon className="absolute left-3 top-3.5 h-5 w-5 text-gray-400" />
                <input
                  type="text"
                  placeholder="Buscar eventos..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="input pl-10 text-lg"
                />
              </div>

              {/* Botón de filtros */}
              <button
                onClick={() => setShowFilters(!showFilters)}
                className={`btn ${showFilters ? 'btn-primary' : 'btn-outline'} relative`}
              >
                <FunnelIcon className="h-5 w-5 mr-2" />
                Filtros
                {activeFiltersCount > 0 && (
                  <span className="absolute -top-2 -right-2 bg-red-500 text-white text-xs rounded-full h-6 w-6 flex items-center justify-center">
                    {activeFiltersCount}
                  </span>
                )}
              </button>

              {/* Recargar */}
              <button
                onClick={refetch}
                disabled={eventosLoading}
                className="btn btn-outline"
              >
                {eventosLoading ? <LoadingSpinner size="sm" /> : '🔄'} Actualizar
              </button>
            </div>

            {/* Panel de filtros */}
            {showFilters && (
              <div className="mt-4 p-4 bg-gray-50 rounded-lg animate-slide-down">
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {/* Filtro por categoría */}
                  <div>
                    <label className="label">Categoría</label>
                    <select
                      value={filters.categoria || ''}
                      onChange={(e) => handleCategoryFilter(e.target.value as EventoCategoria || undefined)}
                      className="select"
                    >
                      <option value="">Todas las categorías</option>
                      {getAllCategorias().map(categoria => {
                        const config = getCategoriaConfig(categoria);
                        const count = categorias?.find(c => c.categoria === categoria)?.total_eventos || 0;
                        return (
                          <option key={categoria} value={categoria}>
                            {config.emoji} {categoria} ({count})
                          </option>
                        );
                      })}
                    </select>
                  </div>

                  {/* Filtro por precio */}
                  <div>
                    <label className="label">Precio máximo</label>
                    <select
                      value={filters.precio_max || ''}
                      onChange={(e) => setFilters(prev => ({ 
                        ...prev, 
                        precio_max: e.target.value ? parseInt(e.target.value) : undefined 
                      }))}
                      className="select"
                    >
                      <option value="">Cualquier precio</option>
                      <option value="0">Solo gratuitos</option>
                      <option value="5">Hasta 5€</option>
                      <option value="10">Hasta 10€</option>
                      <option value="15">Hasta 15€</option>
                    </select>
                  </div>

                  {/* Botones de acción */}
                  <div className="flex items-end gap-2">
                    <button
                      onClick={clearFilters}
                      className="btn btn-secondary flex-1"
                    >
                      Limpiar filtros
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </section>

      {/* Contenido principal */}
      <main className="container-wide section-padding">
        {/* Estadísticas rápidas */}
        {!eventosLoading && eventos && (
          <div className="mb-8">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-white rounded-lg p-4 text-center">
                <div className="text-3xl font-bold text-primary-600">
                  {filteredEventos.length}
                </div>
                <div className="text-gray-600">
                  {filteredEventos.length === 1 ? 'Evento encontrado' : 'Eventos encontrados'}
                </div>
              </div>
              <div className="bg-white rounded-lg p-4 text-center">
                <div className="text-3xl font-bold text-green-600">
                  {filteredEventos.filter(e => formatPrice(e.precio) === 'Gratis').length}
                </div>
                <div className="text-gray-600">Eventos gratuitos</div>
              </div>
              <div className="bg-white rounded-lg p-4 text-center">
                <div className="text-3xl font-bold text-purple-600">
                  {new Set(filteredEventos.map(e => e.categoria)).size}
                </div>
                <div className="text-gray-600">
                  {new Set(filteredEventos.map(e => e.categoria)).size === 1 ? 'Categoría' : 'Categorías'}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Estados de carga y error */}
        {eventosLoading && (
          <div className="text-center py-12">
            <LoadingSpinner size="lg" />
            <p className="text-gray-600 mt-4 text-lg">Cargando eventos...</p>
          </div>
        )}

        {eventosError && (
          <div className="text-center py-12">
            <div className="bg-red-50 border border-red-200 rounded-lg p-6 max-w-md mx-auto">
              <h3 className="text-lg font-medium text-red-800 mb-2">
                Error al cargar eventos
              </h3>
              <p className="text-red-600 mb-4">{eventosError}</p>
              <button
                onClick={refetch}
                className="btn btn-primary"
              >
                Intentar de nuevo
              </button>
            </div>
          </div>
        )}

        {/* Lista de eventos */}
        {!eventosLoading && !eventosError && (
          <>
            {filteredEventos.length === 0 ? (
              <div className="text-center py-12">
                <div className="bg-gray-100 rounded-full w-24 h-24 mx-auto mb-4 flex items-center justify-center">
                  <CalendarIcon className="h-12 w-12 text-gray-400" />
                </div>
                <h3 className="text-xl font-medium text-gray-900 mb-2">
                  No hay eventos disponibles
                </h3>
                <p className="text-gray-600 mb-4">
                  {activeFiltersCount > 0 
                    ? 'Prueba ajustando los filtros de búsqueda'
                    : 'En este momento no hay eventos programados'
                  }
                </p>
                {activeFiltersCount > 0 && (
                  <button
                    onClick={clearFilters}
                    className="btn btn-primary"
                  >
                    Ver todos los eventos
                  </button>
                )}
              </div>
            ) : (
              <div className="space-y-6">
                {/* Ordenar eventos por fecha */}
                {filteredEventos
                  .sort((a, b) => new Date(a.fecha_inicio).getTime() - new Date(b.fecha_inicio).getTime())
                  .map((evento, index) => (
                    <div key={evento.id} className="animate-fade-in" style={{ animationDelay: `${index * 50}ms` }}>
                      <EventCard evento={evento} />
                    </div>
                  ))
                }
              </div>
            )}
          </>
        )}

        {/* Información adicional */}
        {!eventosLoading && filteredEventos.length > 0 && (
          <div className="mt-12 bg-blue-50 border border-blue-200 rounded-lg p-6">
            <h3 className="text-lg font-medium text-blue-900 mb-2">
              ℹ️ Información importante
            </h3>
            <ul className="text-blue-800 space-y-1 text-readable">
              <li>• Todos los eventos mostrados son gratuitos o de bajo coste (máximo 15€)</li>
              <li>• La información se actualiza semanalmente desde fuentes oficiales</li>
              <li>• Recomendamos confirmar horarios y disponibilidad antes de asistir</li>
              <li>• Para más información, contacta directamente con el organizador del evento</li>
            </ul>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="bg-gray-900 text-gray-300">
        <div className="container-wide py-8">
          <div className="text-center">
            <h3 className="text-lg font-medium text-white mb-2">
              Eventos Mayores Madrid
            </h3>
            <p className="text-gray-400 mb-4">
              Plataforma dedicada a conectar a nuestros mayores con la cultura y el ocio de la ciudad
            </p>
            <div className="flex justify-center space-x-6 text-sm">
              <a href="/admin" className="link text-gray-400 hover:text-white">
                Panel de Administración
              </a>
              <span className="text-gray-600">|</span>
              <span className="text-gray-400">
                Actualizado semanalmente
              </span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}