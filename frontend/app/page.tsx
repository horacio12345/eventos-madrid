// app/page.tsx - VERSIÓN MEJORADA SIN DUPLICADOS

'use client';

import { useState, useEffect, useMemo } from 'react';
import { MagnifyingGlassIcon, CalendarIcon } from '@heroicons/react/24/outline';
import { useEventos, useCategorias } from '@/lib/api';
import { 
  getAllCategorias, 
  getCategoriaConfig, 
  formatDateLong, 
  getRelativeDate, 
  formatPrice,
  filterEventos,
  debounce,
  isToday, isTomorrow, isThisWeek, isUpcoming
} from '@/lib/utils';

import EventCard from '@/components/EventCard';
import LoadingSpinner from '@/components/LoadingSpinner';
import type { Evento } from '@/lib/api';

type EventoCategoria = 'Cultura' | 'Deporte y Salud' | 'Formación' | 'Cine' | 'Paseos y Excursiones' | 'Ocio y Social';

interface EventoFilter {
  categoria?: EventoCategoria;
  precio_max?: number;
  busqueda?: string;
}

interface GroupedEvents {
  today: Evento[];
  tomorrow: Evento[];
  thisWeek: Evento[];
  upcoming: Evento[];
}

export default function HomePage() {
  // Estado para filtros
  const [filters, setFilters] = useState<EventoFilter>({});
  const [searchTerm, setSearchTerm] = useState('');
  const [showFilters, setShowFilters] = useState(false);

  // Datos de la API
  const { data: eventos, loading: eventosLoading, error: eventosError, refetch } = useEventos();
  const { data: categorias } = useCategorias();

  // OPTIMIZACIÓN: Usar useMemo en lugar de múltiples useEffect
  // Esto evita renders innecesarios y desincronización de estado
  
  // Debounced search effect
  const debouncedSetFilter = useMemo(
    () => debounce((term: string) => {
      setFilters(prev => ({ ...prev, busqueda: term }));
    }, 300),
    []
  );

  useEffect(() => {
    debouncedSetFilter(searchTerm);
  }, [searchTerm, debouncedSetFilter]);

  // FILTRADO UNIFICADO: Una sola fuente de verdad
  const filteredAndGroupedEventos = useMemo(() => {
    if (!eventos || eventos.length === 0) {
      return {
        filtered: [],
        grouped: { today: [], tomorrow: [], thisWeek: [], upcoming: [] } as GroupedEvents,
        totalCount: 0
      };
    }

    // 1. Aplicar filtros
    const filtered = filterEventos(eventos, filters);
    
    // 2. Agrupar por fechas
    const grouped: GroupedEvents = {
      today: [],
      tomorrow: [],
      thisWeek: [],
      upcoming: [],
    };

    // 3. Ordenar por fecha antes de agrupar
    const sortedEvents = [...filtered].sort((a, b) =>
      new Date(a.fecha_inicio).getTime() - new Date(b.fecha_inicio).getTime()
    );

    // 4. Agrupar eventos sin duplicación
    const processedIds = new Set<string>();
    
    sortedEvents.forEach((evento) => {
      // Crear ID único para evitar duplicados
      const uniqueId = `${evento.id}-${evento.titulo}-${evento.fecha_inicio}`;
      
      if (processedIds.has(uniqueId)) {
        console.warn(`Evento duplicado detectado y omitido: ${evento.titulo}`);
        return;
      }
      
      processedIds.add(uniqueId);
      
      // Agrupar por fecha
      if (isToday(evento.fecha_inicio)) {
        grouped.today.push(evento);
      } else if (isTomorrow(evento.fecha_inicio)) {
        grouped.tomorrow.push(evento);
      } else if (isThisWeek(evento.fecha_inicio)) {
        grouped.thisWeek.push(evento);
      } else if (isUpcoming(evento.fecha_inicio)) {
        grouped.upcoming.push(evento);
      }
    });

    return {
      filtered,
      grouped,
      totalCount: filtered.length
    };
  }, [eventos, filters]);

  // Destructurar resultados
  const { filtered: filteredEventos, grouped: groupedEventos, totalCount } = filteredAndGroupedEventos;

  // Handlers
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
          <div className="py-3">
            <div className="text-center">
              <h1 className="text-3xl font-bold text-gray-900 mb-0">
                🗓️ Agenda Activa
              </h1>
              <p className="text-base text-gray-600 max-w-3xl mx-auto mb-0">
                Planes y actividades en tu ciudad, seleccionados para ti.
              </p>
            </div>
          </div>
        </div>
      </header>

      {/* Barra de búsqueda y filtros */}
      <section className="bg-white border-b border-gray-200 sticky top-0 z-40">
        <div className="container-wide">
          <div className="py-3">
            <div className="flex flex-col lg:flex-row gap-3 items-center">
              {/* Búsqueda */}
              <div className="relative flex-1 w-full">
                <MagnifyingGlassIcon className="absolute left-3 top-2.5 h-5 w-5 text-gray-400" />
                <input
                  type="text"
                  placeholder="Buscar eventos..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="input pl-10 text-lg py-2"
                />
              </div>

              {/* Botón de filtros */}
              <button
                onClick={() => setShowFilters(!showFilters)}
                className={`btn btn-primary btn-md w-full lg:w-auto`}
              >
                <MagnifyingGlassIcon className="h-5 w-5 mr-2" />
                Buscar
              </button>
            </div>

            {/* Panel de filtros */}
            {showFilters && (
              <div className="mt-3 p-3 bg-gray-50 rounded-lg animate-slide-down">
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                  {/* Filtro por categoría */}
                  <div>
                    <label className="label text-base">Categoría</label>
                    <select
                      value={filters.categoria || ''}
                      onChange={(e) => handleCategoryFilter(e.target.value as EventoCategoria || undefined)}
                      className="select text-base"
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
                    <label className="label text-base">Precio máximo</label>
                    <select
                      value={filters.precio_max || ''}
                      onChange={(e) => setFilters(prev => ({ 
                        ...prev, 
                        precio_max: e.target.value ? parseInt(e.target.value) : undefined 
                      }))}
                      className="select text-base"
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
                      className="btn btn-secondary btn-md flex-1"
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
      <main className="container-wide py-4">

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
            {/* No hay eventos */}
            {totalCount === 0 && (
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
            )}

            {/* Eventos de Hoy */}
            {groupedEventos.today.length > 0 && (
              <div className="mb-4">
                <h2 className="text-3xl font-bold text-gray-900 mb-3">
                  Hoy ({groupedEventos.today.length})
                </h2>
                <div className="space-y-4">
                  {groupedEventos.today.map((evento, index) => (
                    <div key={`today-${evento.id}-${index}`} className="animate-fade-in" style={{ animationDelay: `${index * 50}ms` }}>
                      <EventCard evento={evento} />
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Eventos de Mañana */}
            {groupedEventos.tomorrow.length > 0 && (
              <div className="mb-4">
                <h2 className="text-3xl font-bold text-gray-900 mb-3">
                  Mañana ({groupedEventos.tomorrow.length})
                </h2>
                <div className="space-y-4">
                  {groupedEventos.tomorrow.map((evento, index) => (
                    <div key={`tomorrow-${evento.id}-${index}`} className="animate-fade-in" style={{ animationDelay: `${index * 50}ms` }}>
                      <EventCard evento={evento} />
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Eventos Esta Semana */}
            {groupedEventos.thisWeek.length > 0 && (
              <div className="mb-4">
                <h2 className="text-3xl font-bold text-gray-900 mb-3">
                  Esta Semana ({groupedEventos.thisWeek.length})
                </h2>
                <div className="space-y-4">
                  {groupedEventos.thisWeek.map((evento, index) => (
                    <div key={`week-${evento.id}-${index}`} className="animate-fade-in" style={{ animationDelay: `${index * 50}ms` }}>
                      <EventCard evento={evento} />
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Próximos Eventos */}
            {groupedEventos.upcoming.length > 0 && (
              <div className="mb-4">
                <h2 className="text-3xl font-bold text-gray-900 mb-3">
                  Próximos Eventos ({groupedEventos.upcoming.length})
                </h2>
                <div className="space-y-4">
                  {groupedEventos.upcoming.map((evento, index) => (
                    <div key={`upcoming-${evento.id}-${index}`} className="animate-fade-in" style={{ animationDelay: `${index * 50}ms` }}>
                      <EventCard evento={evento} />
                    </div>
                  ))}
                </div>
              </div>
            )}
          </>
        )}

        {/* Información adicional */}
        {!eventosLoading && totalCount > 0 && (
          <div className="mt-12 bg-blue-50 border border-blue-200 rounded-lg p-6">
            <h3 className="text-lg font-medium text-blue-900 mb-2">
              ℹ️ Información importante
            </h3>
            <ul className="text-blue-800 space-y-1 text-readable">
              <li>• Todos los eventos mostrados son gratuitos o de bajo coste (máximo 15€)</li>
              <li>• La información se actualiza semanalmente desde fuentes oficiales</li>
              <li>• Recomendamos confirmar horarios y disponibilidad antes de asistir</li>
              <li>• Para más información, contacta directamente con el organizador del evento</li>
              <li>• Mostrando {totalCount} evento{totalCount !== 1 ? 's' : ''} {activeFiltersCount > 0 ? 'filtrados' : ''}</li>
            </ul>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="bg-gray-900 text-gray-300">
        <div className="container-wide py-8">
          <div className="text-center">
            <h3 className="text-lg font-medium text-white mb-2">
              Agenda Activa
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