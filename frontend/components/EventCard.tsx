// components/EventCard.tsx - VERSIÓN OPTIMIZADA PARA PERSONAS MAYORES

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
  const precio = formatPrice(evento.precio);
  
  // Determinar urgencia de la fecha con estilos mejorados
  const getDateUrgency = () => {
    if (isToday(evento.fecha_inicio)) return 'today';
    if (isTomorrow(evento.fecha_inicio)) return 'tomorrow';
    if (isThisWeek(evento.fecha_inicio)) return 'week';
    return 'future';
  };
  
  const dateUrgency = getDateUrgency();
  
  // Estilos mejorados con la nueva paleta
  const dateStyles = {
    today: 'bg-red-100 text-red-900 border-red-300 font-bold shadow-md',
    tomorrow: 'bg-orange-100 text-orange-900 border-orange-300 font-bold shadow-md',
    week: 'bg-yellow-100 text-yellow-900 border-yellow-300 font-semibold',
    future: 'bg-gray-100 text-gray-800 border-gray-300'
  };

  const extractedDetails = extractEventDetails(evento.descripcion || '', evento.datos_extra);

  const IconComponent = ({ iconName }: { iconName: string }) => {
    const iconProps = "h-6 w-6 text-muted-500 flex-shrink-0";
    
    switch (iconName) {
      case 'ClockIcon': return <ClockIcon className={iconProps} />;
      case 'MapIcon': return <MapPinIcon className={iconProps} />;
      case 'UserGroupIcon': return <UserGroupIcon className={iconProps} />;
      case 'PencilSquareIcon': return <PencilSquareIcon className={iconProps} />;
      default: return null;
    }
  };

  return (
    <article className="card hover:shadow-lg transition-all duration-300 relative overflow-hidden animate-fade-in group">
      
      {/* Indicador visual de urgencia - más visible */}
      {dateUrgency === 'today' && (
        <div className="absolute top-0 left-0 right-0 h-2 bg-gradient-to-r from-red-500 via-orange-500 to-red-500 animate-pulse-gentle"></div>
      )}
      {dateUrgency === 'tomorrow' && (
        <div className="absolute top-0 left-0 right-0 h-2 bg-gradient-to-r from-orange-500 via-yellow-500 to-orange-500"></div>
      )}

      {/* Header mejorado con mejor contraste */}
      <div className="flex items-start justify-between mb-6">
        <div className="flex items-center gap-3 flex-1">
          {/* Categoría con emoji más grande */}
          <div className="flex items-center gap-2 bg-primary/10 px-4 py-2 rounded-xl border-2 border-primary/20">
            <span className="text-2xl">{categoriaConfig.emoji}</span>
            <span className="text-lg font-bold text-primary">
              {evento.categoria}
            </span>
          </div>
          
          {/* Indicador de urgencia más visible */}
          {(dateUrgency === 'today' || dateUrgency === 'tomorrow') && (
            <div className={`flex items-center gap-2 px-4 py-2 rounded-xl border-2 ${dateStyles[dateUrgency]} animate-gentle-bounce`}>
              <ClockIcon className="h-5 w-5" />
              <span className="text-base font-bold">
                {dateUrgency === 'today' ? '¡HOY!' : '¡MAÑANA!'}
              </span>
            </div>
          )}
        </div>
        
        {/* Precio más visible */}
        <div className="text-right flex-shrink-0">
          <div className={`inline-flex items-center gap-2 px-6 py-3 rounded-xl font-bold text-xl border-2 shadow-md ${
            precio === 'Gratis' 
              ? 'bg-success text-white border-success shadow-success/20' 
              : 'bg-accent text-accent-foreground border-accent-foreground/20'
          }`}>
            {precio === 'Gratis' ? (
              <>
                <StarIcon className="h-6 w-6" />
                <span>GRATIS</span>
              </>
            ) : (
              <>
                <CurrencyEuroIcon className="h-6 w-6" />
                <span>{precio}</span>
              </>
            )}
          </div>
        </div>
      </div>

      {/* Título más grande y legible */}
      <h2 className="text-2xl font-bold text-foreground mb-6 leading-tight group-hover:text-primary transition-colors">
        {evento.titulo}
      </h2>

      {/* Información principal con mejor espaciado */}
      <div className="space-y-4 mb-6">
        {/* Fecha con mejor diseño */}
        <div className="flex items-start gap-4">
          <div className="flex-shrink-0 p-2 bg-primary/10 rounded-xl">
            <CalendarIcon className="h-7 w-7 text-primary" />
          </div>
          <div className="flex-1">
            <div className={`inline-flex items-center px-4 py-2 rounded-xl text-lg font-bold border-2 ${dateStyles[dateUrgency]} mb-2`}>
              {fechaRelativa}
            </div>
            <div className="text-xl font-bold text-foreground">
              {fechaCompleta}
            </div>
            {evento.fecha_fin && evento.fecha_fin !== evento.fecha_inicio && (
              <div className="text-lg text-muted mt-1">
                Hasta: {formatDateLong(evento.fecha_fin)}
              </div>
            )}
          </div>
        </div>

        {/* Ubicación con botón de mapa más grande */}
        {evento.ubicacion && (
          <div className="flex items-start gap-4">
            <div className="flex-shrink-0 p-2 bg-accent/20 rounded-xl">
              <MapPinIcon className="h-7 w-7 text-accent-foreground" />
            </div>
            <div className="flex-1 flex items-center justify-between gap-4">
              <div className="text-lg font-medium text-foreground">
                {evento.ubicacion}
              </div>
              <a
                href={`https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(evento.ubicacion)}`}
                target="_blank"
                rel="noopener noreferrer"
                className="btn btn-primary btn-sm shrink-0"
              >
                <MapPinIcon className="h-5 w-5" />
                Ver Mapa
              </a>
            </div>
          </div>
        )}
      </div>

      {/* Detalles extraídos con mejor diseño */}
      {extractedDetails.length > 0 && (
        <div className="mb-6 p-4 bg-secondary/30 rounded-xl border border-secondary">
          <h4 className="text-lg font-semibold text-foreground mb-3">📋 Información Adicional</h4>
          <div className="space-y-2">
            {extractedDetails.map((detail, index) => (
              <div key={index} className="flex items-center gap-3 text-base">
                {detail.icon && <IconComponent iconName={detail.icon} />}
                <span className="font-semibold text-foreground">{detail.label}:</span>
                <span className="text-foreground">{detail.value}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Descripción más legible */}
      {evento.descripcion && (
        <div className="mb-6 p-4 bg-muted/10 rounded-xl">
          <h4 className="text-lg font-semibold text-foreground mb-2">📝 Descripción</h4>
          <div className="text-lg text-foreground leading-relaxed">
            {evento.descripcion}
          </div>
        </div>
      )}

      {/* Footer con mejor diseño */}
      <div className="pt-4 border-t-2 border-primary/10 flex flex-col gap-4">
        {/* Fuente */}
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 bg-primary rounded-full"></div>
          <span className="text-base font-medium text-muted">
            Fuente: {evento.fuente_nombre}
          </span>
        </div>
        
        {/* Botones de acción más grandes */}
        <div className="flex flex-col sm:flex-row gap-3">
          {/* Botón de información */}
          {evento.url_original && (
            <a
              href={evento.url_original}
              target="_blank"
              rel="noopener noreferrer"
              className="btn btn-outline flex-1 justify-center"
            >
              <svg className="h-5 w-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
              </svg>
              Más Información
            </a>
          )}
          
          {/* Botón de compartir (futuro) */}
          <button className="btn btn-secondary flex-1 justify-center">
            <svg className="h-5 w-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.367 2.684 3 3 0 00-5.367-2.684z" />
            </svg>
            Compartir
          </button>
        </div>
      </div>

      {/* Decoración sutil en hover */}
      <div className="absolute -top-2 -right-2 w-8 h-8 bg-primary/20 rounded-full opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
      <div className="absolute -bottom-2 -left-2 w-6 h-6 bg-accent/30 rounded-full opacity-0 group-hover:opacity-100 transition-opacity duration-300 delay-100"></div>
    </article>
  );
}