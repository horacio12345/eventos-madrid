// globals.d.ts

// Tipos globales para la aplicación
declare global {
    interface Window {
      // Extensiones del objeto window si las necesitamos
    }
  }
  
  // Declaraciones de módulos para assets
  declare module '*.svg' {
    const content: React.FunctionComponent<React.SVGAttributes<SVGElement>>;
    export default content;
  }
  
  declare module '*.png' {
    const content: string;
    export default content;
  }
  
  declare module '*.jpg' {
    const content: string;
    export default content;
  }
  
  declare module '*.jpeg' {
    const content: string;
    export default content;
  }
  
  declare module '*.gif' {
    const content: string;
    export default content;
  }
  
  declare module '*.webp' {
    const content: string;
    export default content;
  }
  
  export {};