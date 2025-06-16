// static/js/alpine-init.js
document.addEventListener('alpine:init', () => {
    Alpine.data('secureCookies', () => ({
        accepted: localStorage.getItem('cookie-consent') !== null,
        showSettings: false,
        analyticsEnabled: localStorage.getItem('cookie-analytics') === 'true',

        init() {
            if (this.accepted) {
                console.log('🍪 Cookies ya configuradas previamente');
            } else {
                console.log('🍪 Primera visita - mostrando banner de cookies');
            }
        },

        acceptAll() {
            this.analyticsEnabled = true;
            this.save('all');
            console.log('✅ Usuario aceptó todas las cookies');
        },

        acceptEssential() {
            this.analyticsEnabled = false;
            this.save('essential');
            console.log('✅ Usuario aceptó solo cookies esenciales');
        },

        saveSettings() {
            this.save('custom');
            this.showSettings = false;
            console.log('⚙️ Usuario configuró cookies manualmente');
        },

        save(type) {
            // Guardar preferencias
            localStorage.setItem('cookie-consent', type);
            localStorage.setItem('cookie-analytics', this.analyticsEnabled ? 'true' : 'false');
            localStorage.setItem('cookie-consent-date', new Date().toISOString());
            
            // Actualizar estado
            this.accepted = true;
            
            // Log para debugging
            console.log('💾 Cookies guardadas:', {
                tipo: type,
                analytics: this.analyticsEnabled,
                fecha: new Date().toISOString()
            });
            
            // Cargar analytics si está habilitado
            if (this.analyticsEnabled) {
                this.loadAnalytics();
            }
        },

        loadAnalytics() {
            // Aquí cargarías Google Analytics u otro servicio
            console.log('📊 Cargando analytics anónimos...');
            
            // Ejemplo para Google Analytics 4
            /*
            gtag('config', 'GA_MEASUREMENT_ID', {
                anonymize_ip: true,
                allow_google_signals: false,
                allow_ad_personalization_signals: false
            });
            */
        }
    }));
});