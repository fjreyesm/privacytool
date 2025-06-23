// static/js/alpine-init.js

document.addEventListener('alpine:init', () => {

    Alpine.data('secureCookies', () => ({
        accepted: false,
        showSettings: false,
        analyticsEnabled: false,

        init() {
            // Evitar que el panel se abra automáticamente al inicio
            this.showSettings = false;
            
            // Verificar si ya se dieron permisos usando cookies del servidor
            this.checkCookieConsent();
            
            // Si las cookies de analytics ya fueron aceptadas, carga los scripts
            if (this.analyticsEnabled) {
                this.loadAnalytics();
            }
        },

        checkCookieConsent() {
            // Leer el estado desde cookies del documento
            const consent = this.getCookie('cookie-consent');
            const analytics = this.getCookie('cookie-analytics');
            
            this.accepted = consent !== null && consent !== '';
            this.analyticsEnabled = analytics === 'true';
        },

        getCookie(name) {
            const value = `; ${document.cookie}`;
            const parts = value.split(`; ${name}=`);
            if (parts.length === 2) return parts.pop().split(';').shift();
            return null;
        },

        setCookie(name, value, days = 365) {
            const expires = new Date();
            expires.setTime(expires.getTime() + (days * 24 * 60 * 60 * 1000));
            document.cookie = `${name}=${value};expires=${expires.toUTCString()};path=/;SameSite=Lax`;
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
            // Guardar en cookies en lugar de localStorage
            this.setCookie('cookie-consent', type);
            this.setCookie('cookie-analytics', this.analyticsEnabled);
            this.setCookie('cookie-consent-date', new Date().toISOString());
            
            this.accepted = true;
            
            if (this.analyticsEnabled) {
                this.loadAnalytics();
            }

            // Opcional: enviar al servidor para persistencia
            this.sendConsentToServer(type);
        },

        sendConsentToServer(type) {
            // Enviar via HTMX o fetch al backend Django
            fetch('/api/cookie-consent/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').content
                },
                body: JSON.stringify({
                    consent_type: type,
                    analytics_enabled: this.analyticsEnabled,
                    timestamp: new Date().toISOString()
                })
            }).catch(err => console.log('Consent sync failed:', err));
        },

        loadAnalytics() {
            console.log('📊 Cargando scripts de analytics...');
            // Aquí iría el código real para cargar Google Analytics, etc.
            
            // Ejemplo: Google Analytics 4
            // if (typeof gtag === 'undefined') {
            //     const script = document.createElement('script');
            //     script.src = 'https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID';
            //     document.head.appendChild(script);
            // }
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