// components/EventCard.tsx

'use client';

import { useState } from 'react';
import { 
  CalendarIcon, 
  MapPinIcon, 
  CurrencyEuroIcon,
  ChevronDownIcon,
  ChevronUpIcon,
  ClockIcon
} from '@heroicons/react/24/outline';
import { 
  getCategoriaConfig, 
  formatDateLong, 
  getRelativeDate, 
  formatPrice,
  truncateText,
  isToday,
  isTomorrow,
  isThisWeek
} from '@/lib/utils';
import type { Evento } from '@/lib/api';

interface EventCardProps {
  evento: Evento;
  compact?: boolean;
}

export default function EventCard({ evento, compact = false }: EventCardProps) {
  const [expanded, setExpanded] = useState(false);
  
  const categoriaConfig = getCategoriaConfig(evento.categoria);
  const fechaRelativa = getRelativeDate(evento.fecha_inicio);
  const fechaCompleta = formatDateLong(evento.fecha_inicio);
  const precio = formatPrice(evento.precio);
  
  // Determinar urgencia de la fecha
  const getDateUrgency = () => {
    if (isToday(evento.fecha_inicio)) return 'today';
    if (isTomorrow(evento.fecha_inicio)) return 'tomorrow';
    if (isThisWeek(evento.fecha_inicio)) return 'week';
    return 'future';
  };
  
  const dateUrgency = getDateUrgency();
  
  const dateStyles = {
    today: 'bg-red-100 text-red-800 border-red-200 font-semibold',
    tomorrow: 'bg-orange-100 text-orange-800 border-orange-200 font-semibold',
    week: 'bg-yellow-100 text-yellow-800 border-yellow-200',
    future: 'bg-gray-100 text-gray-700 border-gray-200'
  };

  return (
    <article className={`card hover:shadow-lg transition-all duration-300 ${compact ? 'p-4' : ''}`}>
      {/* Header con categoría y precio */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <span className={`badge badge-lg ${categoriaConfig.color}`}>
            <span className="text-lg mr-2">{categoriaConfig.emoji}</span>
            {evento.categoria}
          </span>
          
          {/* Indicador de urgencia de fecha */}
          {(dateUrgency === 'today' || dateUrgency === 'tomorrow') && (
            <span className={`badge ${dateStyles[dateUrgency]} animate-pulse-gentle`}>
              <ClockIcon className="h-4 w-4 mr-1" />
              {dateUrgency === 'today' ? '¡HOY!' : '¡MAÑANA!'}
            </span>
          )}
        </div>
        
        <div className="text-right">
          <div className={`inline-flex items-center px-3 py-1 rounded-lg font-medium text-lg ${
            precio === 'Gratis' 
              ? 'bg-green-100 text-green-800 border border-green-200' 
              : 'bg-blue-100 text-blue-800 border border-blue-200'
          }`}>
            {precio === 'Gratis' ? (
              <span>🎯 Gratis</span>
            ) : (
              <>
                <CurrencyEuroIcon className="h-4 w-4 mr-1" />
                {precio}
              </>
            )}
          </div>
        </div>
      </div>

      {/* Título del evento */}
      <h2 className="text-xl-readable text-gray-900 mb-4 leading-tight">
        {evento.titulo}
      </h2>

      {/* Información principal */}
      <div className="space-y-3 mb-4">
        {/* Fecha */}
        <div className="flex items-start gap-3">
          <CalendarIcon className="h-6 w-6 text-gray-400 mt-0.5 flex-shrink-0" />
          <div>
            <div className={`inline-flex items-center px-2 py-1 rounded-lg text-sm font-medium border ${dateStyles[dateUrgency]}`}>
              {fechaRelativa}
            </div>
            <div className="text-gray-600 mt-1 text-readable">
              {fechaCompleta}
            </div>
            {evento.fecha_fin && evento.fecha_fin !== evento.fecha_inicio && (
              <div className="text-gray-500 text-sm mt-1">
                Hasta: {formatDateLong(evento.fecha_fin)}
              </div>
            )}
          </div>
        </div>

        {/* Ubicación */}
        {evento.ubicacion && (
          <div className="flex items-start gap-3">
            <MapPinIcon className="h-6 w-6 text-gray-400 mt-0.5 flex-shrink-0" />
            <div className="text-readable text-gray-700">
              {evento.ubicacion}
            </div>
          </div>
        )}
      </div>

      {/* Descripción */}
      {evento.descripcion && (
        <div className="mb-4">
          <div className="text-readable text-gray-700 leading-relaxed">
            {expanded 
              ? evento.descripcion 
              : truncateText(evento.descripcion, compact ? 100 : 200)
            }
          </div>
          
          {evento.descripcion.length > (compact ? 100 : 200) && (
            <button
              onClick={() => setExpanded(!expanded)}
              className="mt-2 text-primary-600 hover:text-primary-800 font-medium text-sm flex items-center gap-1 focus-ring rounded"
            >
              {expanded ? (
                <>
                  <ChevronUpIcon className="h-4 w-4" />
                  Ver menos
                </>
              ) : (
                <>
                  <ChevronDownIcon className="h-4 w-4" />
                  Ver más
                </>
              )}
            </button>
          )}
        </div>
      )}

      {/* Información adicional expandible */}
      {expanded && evento.datos_extra && Object.keys(evento.datos_extra).length > 0 && (
        <div className="mb-4 p-4 bg-gray-50 rounded-lg">
          <h4 className="font-medium text-gray-900 mb-2">Información adicional:</h4>
          <div className="space-y-1 text-sm text-gray-600">
            {Object.entries(evento.datos_extra).map(([key, value]) => (
              <div key={key} className="flex">
                <span className="font-medium capitalize mr-2">{key}:</span>
                <span>{String(value)}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Footer con fuente */}
      <div className="pt-4 border-t border-gray-100 flex items-center justify-between">
        <div className="text-sm text-gray-500">
          <span className="font-medium">Fuente:</span> {evento.fuente_nombre}
        </div>
        
        {/* Botones de acción */}
        <div className="flex items-center gap-2">
          {/* Botón para más información */}
          {evento.url_original && (
            <a
              href={evento.url_original}
              target="_blank"
              rel="noopener noreferrer"
              className="btn btn-outline btn-sm"
            >
              🔗 Más info
            </a>
          )}
          
          {/* Botón para expandir/contraer en modo compacto */}
          {compact && (
            <button
              onClick={() => setExpanded(!expanded)}
              className="btn btn-outline btn-sm"
            >
              {expanded ? 'Menos detalles' : 'Más detalles'}
            </button>
          )}
        </div>
      </div>

      {/* Indicador visual para eventos urgentes */}
      {dateUrgency === 'today' && (
        <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-red-500 to-orange-500 rounded-t-xl"></div>
      )}
      {dateUrgency === 'tomorrow' && (
        <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-orange-500 to-yellow-500 rounded-t-xl"></div>
      )}
    </article>
  );
}