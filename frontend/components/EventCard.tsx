// components/EventCard.tsx

'use client';

import { 
  CalendarIcon, 
  MapPinIcon, 
  CurrencyEuroIcon,
  ClockIcon,
  UserGroupIcon, // Added for plazas
  PencilSquareIcon // Added for inscripciones
} from '@heroicons/react/24/outline';
import { 
  getCategoriaConfig, 
  formatDateLong, 
  getRelativeDate, 
  formatPrice,
  truncateText,
  isToday,
  isTomorrow,
  isThisWeek,
  extractEventDetails // Added for extracting details
} from '@/lib/utils';
import type { Evento } from '@/lib/api';

interface EventCardProps {
  evento: Evento;
}

export default function EventCard({ evento }: EventCardProps) {
  
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

  const extractedDetails = extractEventDetails(evento.descripcion || '');

  const IconComponent = ({ iconName }: { iconName: string }) => {
    switch (iconName) {
      case 'ClockIcon': return <ClockIcon className="h-5 w-5 text-gray-600 flex-shrink-0" />;
      case 'MapIcon': return <MapPinIcon className="h-5 w-5 text-gray-600 flex-shrink-0" />;
      case 'UserGroupIcon': return <UserGroupIcon className="h-5 w-5 text-gray-600 flex-shrink-0" />;
      case 'PencilSquareIcon': return <PencilSquareIcon className="h-5 w-5 text-gray-600 flex-shrink-0" />;
      default: return null;
    }
  };

  return (
    <article className={`card hover:shadow-lg transition-all duration-300 p-2`}>
      {/* Header con categoría y precio */}
      <div className="flex items-start justify-between mb-1">
        <div className="flex items-center gap-1.5">
          <span className={`text-sm font-semibold ${categoriaConfig.color} px-1.5 py-0.5 rounded-md`}>
            <span className="text-base mr-0.5">{categoriaConfig.emoji}</span>
            {evento.categoria}
          </span>
          
          {/* Indicador de urgencia de fecha */}
          {(dateUrgency === 'today' || dateUrgency === 'tomorrow') && (
            <span className={`text-xs ${dateStyles[dateUrgency]} px-1 py-0.5 rounded-md animate-pulse-gentle`}>
              <ClockIcon className="h-3 w-3 mr-0.5 inline-block align-middle" />
              {dateUrgency === 'today' ? '¡HOY!' : '¡MAÑANA!'}
            </span>
          )}
        </div>
        
        <div className="text-right">
          <div className={`inline-flex items-center px-2 py-0.5 rounded-md font-bold text-base ${
            precio === 'Gratis' 
              ? 'bg-green-100 text-green-800 border border-green-200' 
              : 'bg-blue-100 text-blue-800 border border-blue-200'
          }`}>
            {precio === 'Gratis' ? (
              <span>🎯 Gratis</span>
            ) : (
              <>
                <CurrencyEuroIcon className="h-4 w-4 mr-0.5 inline-block align-middle" />
                {precio}
              </>
            )}
          </div>
        </div>
      </div>

      {/* Título del evento */}
      <h2 className="text-xl font-bold text-gray-900 mb-1 leading-snug">
        {evento.titulo}
      </h2>

      {/* Información principal */}
      <div className="space-y-1 mb-1">
        {/* Fecha */}
        <div className="flex items-start gap-2">
          <CalendarIcon className="h-5 w-5 text-gray-600 flex-shrink-0" />
          <div>
            <div className={`inline-flex items-center px-1 py-0.5 rounded-md text-sm font-semibold border ${dateStyles[dateUrgency]}`}>
              {fechaRelativa}
            </div>
            <div className="text-base text-gray-700 font-bold mt-0">
              {fechaCompleta}
            </div>
            {evento.fecha_fin && evento.fecha_fin !== evento.fecha_inicio && (
              <div className="text-sm text-gray-600 mt-0">
                Hasta: {formatDateLong(evento.fecha_fin)}
              </div>
            )}
          </div>
        </div>

        {/* Ubicación y botón de mapa */}
        {evento.ubicacion && (
          <div className="flex items-center justify-between gap-2">
            <div className="flex items-start gap-2 flex-1">
              <MapPinIcon className="h-5 w-5 text-gray-600 flex-shrink-0" />
              <div className="text-base text-gray-700">
                {evento.ubicacion}
              </div>
            </div>
            <a
              href={`https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(evento.ubicacion)}`}
              target="_blank"
              rel="noopener noreferrer"
              className="btn btn-primary btn-xs flex items-center justify-center gap-0.5"
            >
              <MapPinIcon className="h-3 w-3" />
              Mapa
            </a>
          </div>
        )}
      </div>

      {/* Detalles extraídos de la descripción */}
      {extractedDetails.length > 0 && (
        <div className="mb-1 p-1.5 bg-gray-50 rounded-lg">
          <div className="space-y-0.5 text-sm text-gray-700">
            {extractedDetails.map((detail, index) => (
              <div key={index} className="flex items-center gap-1.5">
                {detail.icon && <IconComponent iconName={detail.icon} />}
                <span className="font-semibold">{detail.label}:</span>
                <span>{detail.value}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Descripción */}
      {evento.descripcion && (
        <div className="mb-1">
          <div className="text-sm text-gray-700 leading-relaxed">
            {evento.descripcion}
          </div>
        </div>
      )}

      {/* Información adicional expandible */}
      {evento.datos_extra && Object.keys(evento.datos_extra).length > 0 && (
        <div className="mb-1 p-1.5 bg-gray-50 rounded-lg">
          <h4 className="font-medium text-gray-900 mb-0.5">Información adicional:</h4>
          <div className="space-y-0 text-xs text-gray-700">
            {Object.entries(evento.datos_extra).map(([key, value]) => (
              <div key={key} className="flex">
                <span className="font-medium capitalize mr-0.5">{key}:</span>
                <span>{String(value)}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Footer con fuente */}
      <div className="pt-1.5 border-t border-gray-100 flex flex-col sm:flex-row items-center justify-between gap-1.5">
        <div className="text-xs text-gray-600">
          <span className="font-semibold">Fuente:</span> {evento.fuente_nombre}
        </div>
        
        {/* Botones de acción */}
        <div className="flex items-center gap-1.5">
          {/* Botón para más información */}
          {evento.url_original && (
            <a
              href={evento.url_original}
              target="_blank"
              rel="noopener noreferrer"
              className="btn btn-secondary btn-xs flex-1 sm:flex-none"
            >
              🔗 Más información
            </a>
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