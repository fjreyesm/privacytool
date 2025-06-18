// static/js/alpine-init.js

document.addEventListener('alpine:init', () => {

    Alpine.data('secureCookies', () => ({
        accepted: localStorage.getItem('cookie-consent') !== null,
        showSettings: false,
        analyticsEnabled: localStorage.getItem('cookie-analytics') === 'true',

        init() {
            // Evitar que el panel se abra automáticamente al inicio
            this.showSettings = false;
            
            // Si las cookies de analytics ya fueron aceptadas, carga los scripts
            if (this.analyticsEnabled) {
                this.loadAnalytics();
            }
        },

        // Método para abrir configuración desde eventos externos
        openSettings() {
            this.showSettings = true;
        },

        acceptAll() {
            this.analyticsEnabled = true;
            this.save('all');
        },

        acceptEssential() {
            this.analyticsEnabled = false;
            this.save('essential');
        },

        saveSettings() {
            this.save('custom');
            this.showSettings = false;
        },

        save(type) {
            localStorage.setItem('cookie-consent', type);
            localStorage.setItem('cookie-analytics', this.analyticsEnabled);
            localStorage.setItem('cookie-consent-date', new Date().toISOString());
            
            this.accepted = true;
            
            if (this.analyticsEnabled) {
                this.loadAnalytics();
            }
        },

        loadAnalytics() {
            console.log('📊 Cargando scripts de analytics...');
            // Aquí iría el código real para cargar Google Analytics, etc.
        }
    }));

    // Listener global para abrir configuración de cookies
    window.addEventListener('open-cookie-settings', () => {
        // Buscar la instancia de Alpine y abrir configuración
        const cookieComponent = document.querySelector('[x-data*="secureCookies"]');
        if (cookieComponent && cookieComponent._x_dataStack) {
            cookieComponent._x_dataStack[0].openSettings();
        }
    });
});