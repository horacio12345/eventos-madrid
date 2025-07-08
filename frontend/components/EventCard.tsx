// components/EventCard.tsx

'use client';

import { 
  CalendarIcon, 
  MapPinIcon, 
  CurrencyEuroIcon,
  ClockIcon,
  UserGroupIcon,
  PencilSquareIcon,
  StarIcon
} from '@heroicons/react/24/outline';
import { 
  getCategoriaConfig, 
  formatDateLong, 
  getRelativeDate, 
  formatPrice,
  isToday,
  isTomorrow,
  isThisWeek,
  extractEventDetails
} from '@/lib/utils';
import type { Evento } from '@/lib/api';

interface EventCardProps {
  evento: Evento;
}

export default function EventCard({ evento }: EventCardProps) {
  
  const categoriaConfig = getCategoriaConfig(evento.categoria);
  const fechaRelativa = getRelativeDate(evento.fecha_inicio);
  const fechaCompleta = formatDateLong(evento.fecha_inicio);
  const precio = formatPrice(evento.precio) || 'Gratis';
  
  // Determinar urgencia de la fecha
  const getDateUrgency = () => {
    if (isToday(evento.fecha_inicio)) return 'today';
    if (isTomorrow(evento.fecha_inicio)) return 'tomorrow';
    if (isThisWeek(evento.fecha_inicio)) return 'week';
    return 'future';
  };
  
  const dateUrgency = getDateUrgency();
  
  // Estilos de fecha
  const dateStyles = {
    today: 'bg-red-100 text-red-900 border-red-300 font-bold shadow-md',
    tomorrow: 'bg-orange-100 text-orange-900 border-orange-300 font-bold shadow-md',
    week: 'bg-yellow-100 text-yellow-900 border-yellow-300 font-semibold',
    future: 'bg-gray-100 text-gray-800 border-gray-300'
  };

  const extractedDetails = extractEventDetails ? extractEventDetails(evento.descripcion || '', evento.datos_extra) : [];

  const IconComponent = ({ iconName }: { iconName: string }) => {
    const iconProps = "h-4 w-4 text-muted-500 flex-shrink-0";
    
    switch (iconName) {
      case 'ClockIcon': return <ClockIcon className={iconProps} />;
      case 'MapIcon': return <MapPinIcon className={iconProps} />;
      case 'UserGroupIcon': return <UserGroupIcon className={iconProps} />;
      case 'PencilSquareIcon': return <PencilSquareIcon className={iconProps} />;
      default: return null;
    }
  };

  return (
    <article className="card transition-all duration-300 relative overflow-hidden animate-fade-in">
      
      {/* Indicador visual de urgencia */}
      {dateUrgency === 'today' && (
        <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-red-500 via-orange-500 to-red-500 animate-pulse-gentle"></div>
      )}
      {dateUrgency === 'tomorrow' && (
        <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-orange-500 via-yellow-500 to-orange-500"></div>
      )}

      {/* Header */}
      <div className="flex items-start justify-between mb-2">
        <div className="flex items-center gap-2 flex-1">
          {/* Categoría */}
          <div className="flex items-center gap-1.5 bg-primary/10 px-2 py-1 rounded-md border border-primary/20">
            <span className="text-sm">{categoriaConfig.emoji}</span>
            <span className="text-sm font-bold text-primary">
              {evento.categoria}
            </span>
          </div>
          
          {/* Indicador de urgencia */}
          {(dateUrgency === 'today' || dateUrgency === 'tomorrow') && (
            <div className={`flex items-center gap-1 px-2 py-0.5 rounded-md border text-xs ${dateStyles[dateUrgency]}`}>
              <ClockIcon className="h-3 w-3" />
              <span className="font-bold">
                {dateUrgency === 'today' ? '¡HOY!' : '¡MAÑANA!'}
              </span>
            </div>
          )}
        </div>
        
        {/* Precio */}
        <div className="text-right flex-shrink-0">
          <div className={`inline-flex items-center gap-1 px-2 py-1 rounded-md font-bold text-sm border ${
            (precio === 'Gratis' || !precio || precio.trim() === '') 
              ? 'bg-green-600 text-white border-green-600' 
              : 'bg-blue-100 text-blue-800 border-blue-200'
          }`}>
            {(precio === 'Gratis' || !precio || precio.trim() === '') ? (
              <>
                <StarIcon className="h-3 w-3" />
                <span>GRATIS</span>
              </>
            ) : (
              <>
                <CurrencyEuroIcon className="h-3 w-3" />
                <span>{precio}</span>
              </>
            )}
          </div>
        </div>
      </div>

      {/* Título */}
      <h2 className="text-base font-bold text-foreground mb-2 leading-tight">
        {evento.titulo}
      </h2>

      {/* Información principal */}
      <div className="space-y-2 mb-2">
        {/* Fecha */}
        <div className="flex items-start gap-2">
          <div className="flex-shrink-0 p-1 bg-primary/10 rounded-md">
            <CalendarIcon className="h-4 w-4 text-primary" />
          </div>
          <div className="flex-1">
            <div className={`inline-flex items-center px-2 py-0.5 rounded-md text-xs font-bold border ${dateStyles[dateUrgency]} mb-1`}>
              {fechaRelativa}
            </div>
            <div className="text-sm font-bold text-foreground">
              {fechaCompleta}
            </div>
            {evento.fecha_fin && evento.fecha_fin !== evento.fecha_inicio && (
              <div className="text-xs text-muted mt-0.5">
                Hasta: {formatDateLong(evento.fecha_fin)}
              </div>
            )}
          </div>
        </div>

        {/* Ubicación */}
        {evento.ubicacion && (
          <div className="flex items-start gap-2">
            <div className="flex-shrink-0 p-1 bg-accent/20 rounded-md">
              <MapPinIcon className="h-4 w-4 text-accent-foreground" />
            </div>
            <div className="flex-1 flex items-center justify-between gap-2">
              <div className="text-sm font-medium text-foreground">
                {evento.ubicacion}
              </div>
              <a
                href={`https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(evento.ubicacion)}`}
                target="_blank"
                rel="noopener noreferrer"
                className="btn btn-primary btn-xs shrink-0"
              >
                <MapPinIcon className="h-3 w-3" />
                Ver Mapa
              </a>
            </div>
          </div>
        )}
      </div>

      {/* Detalles extraídos */}
      {extractedDetails.length > 0 && (
        <div className="mb-2 p-2 bg-secondary/30 rounded-md border border-secondary">
          <h4 className="text-sm font-semibold text-foreground mb-1.5">📋 Información Adicional</h4>
          <div className="space-y-0.5">
            {extractedDetails.map((detail, index) => (
              <div key={index} className="flex items-center gap-1.5 text-xs">
                {detail.icon && <IconComponent iconName={detail.icon} />}
                <span className="font-semibold text-foreground">{detail.label}:</span>
                <span className="text-foreground">{detail.value}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Descripción */}
      {evento.descripcion && (
        <div className="p-2 bg-muted/10 rounded-md">
          <h4 className="text-sm font-semibold text-foreground mb-1.5">📝 Descripción</h4>
          <div className="text-sm text-foreground leading-relaxed">
            {evento.descripcion}
          </div>
        </div>
      )}
    </article>
  );
}