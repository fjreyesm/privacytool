// tailwind.config.js

// TEMA POR DEFECTO
const defaultTheme = require('tailwindcss/defaultTheme');
const colors = require('tailwindcss/colors');

module.exports = {
    content: [
        './templates/**/*.html',
        './**/templates/**/*.html', 
        './*/templates/**/*.html',
        //  añadir más rutas según cambie la estructura de proyecto
        './static/js/**/*.js', 
    ],
    theme: {
        extend: {
            colors: {
                // COLORES PRINCIPALES NUEVOS - Azul + Morado
                'primary': '#005A9C',               // Azul principal (mantener)
                'primary-light': '#2563eb',         // Azul claro
                'primary-dark': '#1e40af',          // Azul oscuro
                
                // MORADO PROFESIONAL (del email)
                'brand-purple': '#6366f1',          // Morado principal 
                'brand-purple-light': '#818cf8',    // Morado claro
                'brand-purple-dark': '#4f46e5',     // Morado oscuro
                
                // AZULES (mantener compatibilidad)
                'brand-blue': '#005A9C',            // Alias para primary
                'brand-blue-light': '#2563eb',      // Alias para primary-light
                'brand-blue-dark': '#1e40af',       // Alias para primary-dark
                
                // GRISES NEUTROS
                'brand-gray': '#64748b',            // Gris medio
                'brand-gray-light': '#f1f5f9',      // Gris muy claro
                'brand-gray-dark': '#334155',       // Gris oscuro
                
                // COLORES EXISTENTES (mantener compatibilidad)
                'secondary': '#6c757d',
                'secure-green': '#10B981',          // Verde seguridad
                'secure-white': '#FFFFFF',          // Blanco para tarjetas
                'secure-gray': '#F3F4F6',           // Gris claro para fondos

                // COLORES SEMÁNTICOS (mejorados)
                'success': '#10b981',               // Verde éxito
                'danger': '#ef4444',                // Rojo peligro  
                'warning': '#f59e0b',               // Amarillo advertencia
                'info': '#06b6d4',                  // Cian información
                
                // GRADIENTES HELPER (para usar en CSS)
                'gradient-start': '#005A9C',        // Inicio gradiente
                'gradient-end': '#6366f1',          // Final gradiente
            },
            fontFamily: {
                'sans': ['Roboto', ...defaultTheme.fontFamily.sans],
            },
            // GRADIENTES PERSONALIZADOS
            backgroundImage: {
                'gradient-brand': 'linear-gradient(135deg, #005A9C 0%, #6366f1 100%)',
                'gradient-brand-soft': 'linear-gradient(135deg, #005A9C 0%, #2563eb 50%, #6366f1 100%)',
                'gradient-security': 'linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%)',
            },
            // SOMBRAS PERSONALIZADAS
            boxShadow: {
                'brand': '0 4px 14px 0 rgba(0, 90, 156, 0.15)',
                'brand-lg': '0 10px 25px -3px rgba(0, 90, 156, 0.1), 0 4px 6px -2px rgba(0, 90, 156, 0.05)',
                'purple': '0 4px 14px 0 rgba(99, 102, 241, 0.15)',
                'purple-lg': '0 10px 25px -3px rgba(99, 102, 241, 0.1), 0 4px 6px -2px rgba(99, 102, 241, 0.05)',
            }
        },
    },
    plugins: [
        require('@tailwindcss/typography'),
        require('@tailwindcss/aspect-ratio'),
        require('@tailwindcss/forms'),
    ],
};