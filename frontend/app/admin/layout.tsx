// app/admin/layout.tsx

'use client';

import { useState, useEffect } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import Link from 'next/link';
import { 
  HomeIcon,
  Cog6ToothIcon,
  GlobeAltIcon,
  DocumentTextIcon,
  ArrowRightOnRectangleIcon,
  Bars3Icon,
  XMarkIcon,
  ChevronDownIcon
} from '@heroicons/react/24/outline';
import { api } from '@/lib/api';
import { cn } from '@/lib/utils';
import LoadingSpinner from '@/components/LoadingSpinner';

interface AdminLayoutProps {
  children: React.ReactNode;
}

export default function AdminLayout({ children }: AdminLayoutProps) {
  const router = useRouter();
  const pathname = usePathname();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);

  // Verificar autenticación
  useEffect(() => {
    const checkAuth = async () => {
      try {
        const token = api.auth.isLoggedIn();
        if (!token) {
          router.push('/admin/login');
          return;
        }
        
        // Verificar que el token sea válido haciendo una llamada autenticada
        await api.admin.fuentes.getAll();
        setIsAuthenticated(true);
      } catch (error) {
        console.error('Error verificando autenticación:', error);
        api.auth.logout();
        router.push('/admin/login');
      } finally {
        setLoading(false);
      }
    };

    // No verificar auth en página de login
    if (pathname === '/admin/login') {
      setLoading(false);
      return;
    }

    checkAuth();
  }, [pathname, router]);

  const handleLogout = () => {
    api.auth.logout();
    router.push('/admin/login');
  };

  // Navegación del sidebar
  const navigation = [
    {
      name: 'Dashboard',
      href: '/admin/dashboard',
      icon: HomeIcon,
      current: pathname === '/admin/dashboard'
    },
    {
      name: 'Gestión de Fuentes',
      href: '/admin/fuentes',
      icon: GlobeAltIcon,
      current: pathname.startsWith('/admin/fuentes')
    },
    {
      name: 'Logs del Sistema',
      href: '/admin/logs',
      icon: DocumentTextIcon,
      current: pathname === '/admin/logs'
    },
    {
      name: 'Configuración',
      href: '/admin/config',
      icon: Cog6ToothIcon,
      current: pathname === '/admin/config'
    }
  ];

  // Mostrar spinner mientras verifica autenticación
  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <LoadingSpinner size="lg" text="Verificando acceso..." />
      </div>
    );
  }

  // No mostrar layout si no está autenticado (se redirige a login)
  if (!isAuthenticated && pathname !== '/admin/login') {
    return null;
  }

  // Layout especial para página de login
  if (pathname === '/admin/login') {
    return <>{children}</>;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Sidebar móvil */}
      <div className={cn(
        'fixed inset-0 z-50 lg:hidden',
        sidebarOpen ? 'block' : 'hidden'
      )}>
        <div className="fixed inset-0 bg-gray-600 bg-opacity-75" onClick={() => setSidebarOpen(false)} />
        
        <div className="fixed top-0 left-0 h-full w-64 bg-white shadow-xl">
          <div className="flex items-center justify-between p-4 border-b">
            <h2 className="text-lg font-semibold text-gray-900">Panel Admin</h2>
            <button
              onClick={() => setSidebarOpen(false)}
              className="p-2 rounded-md text-gray-400 hover:text-gray-600"
            >
              <XMarkIcon className="h-6 w-6" />
            </button>
          </div>
          
          <nav className="p-4">
            <SidebarNavigation navigation={navigation} />
          </nav>
        </div>
      </div>

      {/* Sidebar desktop */}
      <div className="hidden lg:fixed lg:inset-y-0 lg:flex lg:w-64 lg:flex-col">
        <div className="flex flex-col flex-grow bg-white border-r border-gray-200 pt-5 pb-4 overflow-y-auto">
          <div className="flex items-center flex-shrink-0 px-4">
            <Link href="/" className="flex items-center">
              <span className="text-2xl mr-2">🎭</span>
              <div>
                <h2 className="text-lg font-semibold text-gray-900">Admin Panel</h2>
                <p className="text-sm text-gray-500">Eventos Mayores</p>
              </div>
            </Link>
          </div>
          
          <nav className="mt-8 flex-1 px-4">
            <SidebarNavigation navigation={navigation} />
          </nav>
          
          {/* Logout en sidebar */}
          <div className="px-4 py-3 border-t border-gray-200">
            <button
              onClick={handleLogout}
              className="flex items-center w-full text-left text-sm text-gray-600 hover:text-gray-900 p-2 rounded-lg hover:bg-gray-100"
            >
              <ArrowRightOnRectangleIcon className="h-5 w-5 mr-3" />
              Cerrar Sesión
            </button>
          </div>
        </div>
      </div>

      {/* Contenido principal */}
      <div className="lg:pl-64 flex flex-col flex-1">
        {/* Header móvil */}
        <div className="sticky top-0 z-10 lg:hidden bg-white border-b border-gray-200 px-4 py-2">
          <div className="flex items-center justify-between">
            <button
              onClick={() => setSidebarOpen(true)}
              className="p-2 rounded-md text-gray-400 hover:text-gray-600"
            >
              <Bars3Icon className="h-6 w-6" />
            </button>
            
            <h1 className="text-lg font-semibold text-gray-900">Panel Admin</h1>
            
            <button
              onClick={handleLogout}
              className="p-2 rounded-md text-gray-400 hover:text-gray-600"
            >
              <ArrowRightOnRectangleIcon className="h-6 w-6" />
            </button>
          </div>
        </div>

        {/* Contenido de la página */}
        <main className="flex-1">
          <div className="py-6">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}

// Componente para la navegación del sidebar
function SidebarNavigation({ navigation }: { navigation: any[] }) {
  return (
    <ul className="space-y-1">
      {navigation.map((item) => (
        <li key={item.name}>
          <Link
            href={item.href}
            className={cn(
              'group flex items-center px-3 py-2 text-sm font-medium rounded-lg transition-colors',
              item.current
                ? 'bg-primary-100 text-primary-700'
                : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
            )}
          >
            <item.icon
              className={cn(
                'mr-3 h-5 w-5 flex-shrink-0',
                item.current ? 'text-primary-500' : 'text-gray-400 group-hover:text-gray-500'
              )}
            />
            {item.name}
          </Link>
        </li>
      ))}
    </ul>
  );
}