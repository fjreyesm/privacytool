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
                'primary': '#005A9C',
                'secondary': '#6c757d',
                'secure-green': '#10B981', // ¡Buen añadido!
                'secure-white': '#FFFFFF', // Blanco para tarjetas,
                'secure-gray': '#F3F4F6', // Gris claro para fondos

                // Colores semánticos usando la paleta de Tailwind
                'success': colors.green[600],
                'danger': colors.red[600],
                'warning': colors.amber[500],
                'info': colors.sky[500],
            },
            fontFamily: {
                
                'sans': ['Roboto', ...defaultTheme.fontFamily.sans],
            },
        },
    },
    plugins: [
        require('@tailwindcss/typography'),
        require('@tailwindcss/aspect-ratio'),
        require('@tailwindcss/forms'),
    ],
};