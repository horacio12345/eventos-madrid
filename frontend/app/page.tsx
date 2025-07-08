// app/page.tsx

'use client';

import { useState, useEffect, useMemo } from 'react';
import { MagnifyingGlassIcon, CalendarIcon, AdjustmentsHorizontalIcon, XMarkIcon } from '@heroicons/react/24/outline';
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

  // Filtrado unificado
  const filteredAndGroupedEventos = useMemo(() => {
    if (!eventos || eventos.length === 0) {
      return {
        filtered: [],
        grouped: { today: [], tomorrow: [], thisWeek: [], upcoming: [] } as GroupedEvents,
        totalCount: 0
      };
    }

    // Aplicar filtros
    const filtered = filterEventos(eventos, filters);
    
    // Agrupar por fechas
    const grouped: GroupedEvents = {
      today: [],
      tomorrow: [],
      thisWeek: [],
      upcoming: [],
    };

    // Ordenar por fecha antes de agrupar
    const sortedEvents = [...filtered].sort((a, b) =>
      new Date(a.fecha_inicio).getTime() - new Date(b.fecha_inicio).getTime()
    );

    // Agrupar eventos sin duplicación
    const processedIds = new Set<string>();
    
    sortedEvents.forEach((evento) => {
      const uniqueId = `${evento.id}-${evento.titulo}-${evento.fecha_inicio}`;
      
      if (processedIds.has(uniqueId)) {
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

  const { filtered: filteredEventos, grouped: groupedEventos, totalCount } = filteredAndGroupedEventos;

  // Handlers
  const handleCategoryFilter = (categoria: EventoCategoria | undefined) => {
    setFilters(prev => ({ ...prev, categoria }));
  };

  const clearFilters = () => {
    setFilters({});
    setSearchTerm('');
    setShowFilters(false);
  };

  const activeFiltersCount = Object.values(filters).filter(Boolean).length;

  return (
    <div className="min-h-screen bg-background">
      <header className="bg-card shadow-medium border-b-2 border-primary/10">
        <div className="container-wide">
          <div className="py-4">
            <div className="text-center">
              <h1 className="text-3xl md:text-4xl font-bold text-foreground mb-3 tracking-tight">
                🗓️ Agenda Activa
              </h1>
              <p className="text-lg md:text-xl text-primary max-w-4xl mx-auto leading-relaxed font-medium">
                Planes y actividades en tu ciudad, seleccionados especialmente para ti.
              </p>
            </div>
          </div>
        </div>
      </header>

      {/* Barra de búsqueda mejorada */}
      <section className="bg-card border-b-2 border-primary/10 shadow-soft">
        <div className="container-wide">
          <div className="py-4">
            <div className="max-w-4xl mx-auto">
              <div className="flex flex-col gap-3">
                {/* Búsqueda principal */}
                <div className="relative">
                  <MagnifyingGlassIcon className="absolute left-4 top-1/2 transform -translate-y-1/2 h-6 w-6 text-muted" />
                  <input
                    type="text"
                    placeholder="¿Qué te apetece hacer? Busca eventos..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="input pl-12 pr-4 text-lg py-4 text-center border-2 border-primary/20 focus:border-primary shadow-md"
                    style={{ minHeight: '60px' }}
                  />
                </div>

                {/* Botones de acción */}
                <div className="flex flex-col sm:flex-row gap-2">
                  <button
                    onClick={() => setShowFilters(!showFilters)}
                    className={`btn ${showFilters ? 'btn-primary' : 'btn-secondary'} flex-1 justify-center text-lg`}
                  >
                    <AdjustmentsHorizontalIcon className="h-5 w-5 mr-2" />
                    Filtrar Búsqueda
                    {activeFiltersCount > 0 && (
                      <span className="ml-2 bg-white text-primary rounded-full px-2 py-1 text-sm font-bold">
                        {activeFiltersCount}
                      </span>
                    )}
                  </button>
                  
                  {activeFiltersCount > 0 && (
                    <button
                      onClick={clearFilters}
                      className="btn btn-outline flex-1 sm:flex-none justify-center text-lg"
                    >
                      <XMarkIcon className="h-5 w-5 mr-2" />
                      Limpiar
                    </button>
                  )}
                </div>

                {/* Panel de filtros expandido */}
                {showFilters && (
                  <div className="bg-secondary/20 p-4 rounded-xl border-2 border-secondary animate-slide-down">
                    <h3 className="text-lg font-bold text-foreground mb-4">🔍 Filtrar Eventos</h3>
                    
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                      {/* Filtro por categoría */}
                      <div>
                        <label className="label text-lg mb-3">Tipo de Actividad</label>
                        <select
                          value={filters.categoria || ''}
                          onChange={(e) => handleCategoryFilter(e.target.value as EventoCategoria || undefined)}
                          className="select text-lg py-3"
                        >
                          <option value="">🎭 Todas las actividades</option>
                          {getAllCategorias().map(categoria => {
                            const config = getCategoriaConfig(categoria);
                            const count = categorias?.find(c => c.categoria === categoria)?.total_eventos || 0;
                            return (
                              <option key={categoria} value={categoria}>
                                {config.emoji} {categoria} ({count} eventos)
                              </option>
                            );
                          })}
                        </select>
                      </div>

                      {/* Filtro por precio */}
                      <div>
                        <label className="label text-lg mb-3">Precio Máximo</label>
                        <select
                          value={filters.precio_max || ''}
                          onChange={(e) => setFilters(prev => ({ 
                            ...prev, 
                            precio_max: e.target.value ? parseInt(e.target.value) : undefined 
                          }))}
                          className="select text-lg py-3"
                        >
                          <option value="">💰 Cualquier precio</option>
                          <option value="0">⭐ Solo gratuitos</option>
                          <option value="5">💰 Hasta 5€</option>
                          <option value="10">💰 Hasta 10€</option>
                          <option value="15">💰 Hasta 15€</option>
                        </select>
                      </div>
                    </div>

                    {/* Resumen de filtros */}
                    {activeFiltersCount > 0 && (
                      <div className="mt-4 p-3 bg-primary/10 rounded-lg border border-primary/20">
                        <p className="text-base font-semibold text-primary">
                          📋 Filtros activos: Mostrando {totalCount} eventos
                        </p>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Contenido principal */}
      <main className="container-wide py-5">

        {/* Estados de carga y error */}
        {eventosLoading && (
          <div className="text-center py-12">
            <LoadingSpinner size="lg" />
            <p className="text-muted mt-4 text-lg font-medium">Cargando eventos...</p>
          </div>
        )}

        {eventosError && (
          <div className="text-center py-12">
            <div className="bg-error-bg border-2 border-error rounded-xl p-5 max-w-2xl mx-auto">
              <h3 className="text-lg font-bold text-error mb-3">
                ❌ Error al cargar eventos
              </h3>
              <p className="text-error text-base mb-4">{eventosError}</p>
              <button
                onClick={refetch}
                className="btn btn-primary btn-lg"
              >
                🔄 Intentar de Nuevo
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
                <div className="bg-muted/10 rounded-full w-24 h-24 mx-auto mb-5 flex items-center justify-center">
                  <CalendarIcon className="h-12 w-12 text-muted" />
                </div>
                <h3 className="text-xl font-bold text-foreground mb-3">
                  😔 No hay eventos disponibles
                </h3>
                <p className="text-lg text-muted mb-5 max-w-2xl mx-auto">
                  {activeFiltersCount > 0
                    ? 'No encontramos eventos con esos filtros. Prueba a ampliar tu búsqueda.'
                    : 'En este momento no hay eventos programados. ¡Vuelve pronto!'
                  }
                </p>
                {activeFiltersCount > 0 && (
                  <button
                    onClick={clearFilters}
                    className="btn btn-primary btn-lg"
                  >
                    👀 Ver Todos los Eventos
                  </button>
                )}
              </div>
            )}

            {/* Contador de resultados */}
            {totalCount > 0 && (
              <div className="mb-5 text-center">
                <div className="inline-flex items-center gap-2 bg-primary/10 px-4 py-2 rounded-lg border border-primary/20">
                  <span className="text-lg">📊</span>
                  <span className="text-lg font-bold text-primary">
                    {totalCount} evento{totalCount !== 1 ? 's' : ''} encontrado{totalCount !== 1 ? 's' : ''}
                  </span>
                </div>
              </div>
            )}

            {/* Eventos de Hoy */}
            {groupedEventos.today.length > 0 && (
              <section className="mb-8">
                <div className="flex items-center gap-3 mb-5">
                  <div className="bg-red-100 p-2 rounded-lg">
                    <span className="text-xl">🔥</span>
                  </div>
                  <div>
                    <h2 className="text-2xl font-bold text-foreground">
                      ¡Hoy Mismo!
                    </h2>
                    <p className="text-lg text-muted">
                      {groupedEventos.today.length} evento{groupedEventos.today.length !== 1 ? 's' : ''} para hoy
                    </p>
                  </div>
                </div>
                <div className="space-y-4">
                  {groupedEventos.today.map((evento, index) => (
                    <div key={`today-${evento.id}-${index}`} className="animate-fade-in" style={{ animationDelay: `${index * 100}ms` }}>
                      <EventCard evento={evento} />
                    </div>
                  ))}
                </div>
              </section>
            )}

            {/* Eventos de Mañana */}
            {groupedEventos.tomorrow.length > 0 && (
              <section className="mb-8">
                <div className="flex items-center gap-3 mb-5">
                  <div className="bg-orange-100 p-2 rounded-lg">
                    <span className="text-xl">⏰</span>
                  </div>
                  <div>
                    <h2 className="text-2xl font-bold text-foreground">
                      Mañana
                    </h2>
                    <p className="text-lg text-muted">
                      {groupedEventos.tomorrow.length} evento{groupedEventos.tomorrow.length !== 1 ? 's' : ''} para mañana
                    </p>
                  </div>
                </div>
                <div className="space-y-4">
                  {groupedEventos.tomorrow.map((evento, index) => (
                    <div key={`tomorrow-${evento.id}-${index}`} className="animate-fade-in" style={{ animationDelay: `${index * 100}ms` }}>
                      <EventCard evento={evento} />
                    </div>
                  ))}
                </div>
              </section>
            )}

            {/* Eventos Esta Semana */}
            {groupedEventos.thisWeek.length > 0 && (
              <section className="mb-8">
                <div className="flex items-center gap-3 mb-5">
                  <div className="bg-yellow-100 p-2 rounded-lg">
                    <span className="text-xl">📅</span>
                  </div>
                  <div>
                    <h2 className="text-2xl font-bold text-foreground">
                      Esta Semana
                    </h2>
                    <p className="text-lg text-muted">
                      {groupedEventos.thisWeek.length} evento{groupedEventos.thisWeek.length !== 1 ? 's' : ''} esta semana
                    </p>
                  </div>
                </div>
                <div className="space-y-4">
                  {groupedEventos.thisWeek.map((evento, index) => (
                    <div key={`week-${evento.id}-${index}`} className="animate-fade-in" style={{ animationDelay: `${index * 100}ms` }}>
                      <EventCard evento={evento} />
                    </div>
                  ))}
                </div>
              </section>
            )}

            {/* Próximos Eventos */}
            {groupedEventos.upcoming.length > 0 && (
              <section className="mb-8">
                <div className="flex items-center gap-3 mb-5">
                  <div className="bg-blue-100 p-2 rounded-lg">
                    <span className="text-xl">🔮</span>
                  </div>
                  <div>
                    <h2 className="text-2xl font-bold text-foreground">
                      Próximamente
                    </h2>
                    <p className="text-lg text-muted">
                      {groupedEventos.upcoming.length} evento{groupedEventos.upcoming.length !== 1 ? 's' : ''} próximo{groupedEventos.upcoming.length !== 1 ? 's' : ''}
                    </p>
                  </div>
                </div>
                <div className="space-y-4">
                  {groupedEventos.upcoming.map((evento, index) => (
                    <div key={`upcoming-${evento.id}-${index}`} className="animate-fade-in" style={{ animationDelay: `${index * 100}ms` }}>
                      <EventCard evento={evento} />
                    </div>
                  ))}
                </div>
              </section>
            )}
          </>
        )}

        {/* Información adicional mejorada */}
        {!eventosLoading && totalCount > 0 && (
          <div className="mt-10 bg-accent/20 border-2 border-accent rounded-xl p-5">
            <div className="flex items-start gap-3 mb-4">
              <span className="text-2xl">ℹ️</span>
              <div>
                <h4 className="text-lg font-bold text-accent-foreground mb-2">
                  Información Importante
                </h4>
              </div>
            </div>
            <ul className="text-base text-accent-foreground space-y-2 leading-relaxed">
              <li className="flex items-start gap-2">
                <span className="text-lg">🌟</span>
                <span>Eventos seleccionados especialmente para ti</span>
              </li>

              <li className="flex items-start gap-2">
                <span className="text-lg">✅</span>
                <span>Recomendamos confirmar horarios y disponibilidad antes de asistir</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-lg">📞</span>
                <span>Para más información, contacta directamente con el organizador</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-lg">🔄</span>
                <span>Actualizaciones periódicas con nuevos eventos</span>
              </li>
            </ul>
          </div>
        )}
      </main>

      {/* Footer mejorado */}
      <footer className="bg-foreground text-background mt-12">
        <div className="container-wide py-8">
          <div className="text-center">
            <h3 className="text-xl font-bold mb-3">
              🎭 Agenda Activa
            </h3>
            <p className="text-lg mb-5 max-w-2xl mx-auto leading-relaxed">
              ¡Planes y actividades para disfrutar!
            </p>
            <div className="flex flex-col sm:flex-row justify-center items-center gap-4 text-base">
              <a href="/admin" className="link text-background hover:text-primary-200 font-semibold">
                🔧 Panel de Administración
              </a>
              <span className="hidden sm:block text-background/60">|</span>
              <span className="text-background/80 font-medium">
                📅 Actualizada periódicamente
              </span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}