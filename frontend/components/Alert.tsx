// components/Alert.tsx

import { 
    CheckCircleIcon, 
    ExclamationTriangleIcon, 
    XCircleIcon, 
    InformationCircleIcon,
    XMarkIcon 
  } from '@heroicons/react/24/outline';
  import { cn } from '@/lib/utils';
  
  interface AlertProps {
    type: 'success' | 'error' | 'warning' | 'info';
    title?: string;
    message: string;
    dismissible?: boolean;
    onDismiss?: () => void;
    className?: string;
  }
  
  export default function Alert({ 
    type, 
    title, 
    message, 
    dismissible = false, 
    onDismiss,
    className 
  }: AlertProps) {
    const typeConfig = {
      success: {
        icon: CheckCircleIcon,
        bgColor: 'bg-green-50',
        borderColor: 'border-green-200',
        iconColor: 'text-green-400',
        titleColor: 'text-green-800',
        textColor: 'text-green-700'
      },
      error: {
        icon: XCircleIcon,
        bgColor: 'bg-red-50',
        borderColor: 'border-red-200',
        iconColor: 'text-red-400',
        titleColor: 'text-red-800',
        textColor: 'text-red-700'
      },
      warning: {
        icon: ExclamationTriangleIcon,
        bgColor: 'bg-yellow-50',
        borderColor: 'border-yellow-200',
        iconColor: 'text-yellow-400',
        titleColor: 'text-yellow-800',
        textColor: 'text-yellow-700'
      },
      info: {
        icon: InformationCircleIcon,
        bgColor: 'bg-blue-50',
        borderColor: 'border-blue-200',
        iconColor: 'text-blue-400',
        titleColor: 'text-blue-800',
        textColor: 'text-blue-700'
      }
    };
  
    const config = typeConfig[type];
    const Icon = config.icon;
  
    return (
      <div className={cn(
        'rounded-lg border p-4 animate-fade-in',
        config.bgColor,
        config.borderColor,
        className
      )}>
        <div className="flex">
          <div className="flex-shrink-0">
            <Icon className={cn('h-5 w-5', config.iconColor)} />
          </div>
          
          <div className="ml-3 flex-1">
            {title && (
              <h3 className={cn('text-sm font-medium', config.titleColor)}>
                {title}
              </h3>
            )}
            <div className={cn(
              'text-sm',
              config.textColor,
              title ? 'mt-1' : ''
            )}>
              {message}
            </div>
          </div>
          
          {dismissible && onDismiss && (
            <div className="ml-auto pl-3">
              <div className="-mx-1.5 -my-1.5">
                <button
                  type="button"
                  onClick={onDismiss}
                  className={cn(
                    'inline-flex rounded-md p-1.5 focus:ring-2 focus:ring-offset-2 hover:opacity-75 transition-opacity',
                    config.textColor,
                    'focus:ring-' + type + '-600'
                  )}
                >
                  <span className="sr-only">Cerrar</span>
                  <XMarkIcon className="h-5 w-5" />
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    );
  }