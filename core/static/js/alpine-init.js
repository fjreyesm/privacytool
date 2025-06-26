// static/js/alpine-init.js

document.addEventListener('alpine:init', () => {

    Alpine.data('secureCookies', () => ({
        accepted: false,
        showSettings: false,
        analyticsEnabled: false,

        init() {
            console.log('🍪 Cookie system initialized');
            
            // Verificar estado de cookies
            this.checkCookieConsent();
            
            console.log('Estado inicial:', {
                accepted: this.accepted,
                showSettings: this.showSettings,
                analyticsEnabled: this.analyticsEnabled
            });
        },

        checkCookieConsent() {
            try {
                // Verificar cookies del navegador
                const consent = this.getCookie('cookie-consent');
                this.accepted = consent !== null && consent !== '';
                
                const analytics = this.getCookie('cookie-analytics');
                this.analyticsEnabled = analytics === 'true';
                
                console.log('Verificación cookies:', {
                    consent,
                    accepted: this.accepted,
                    analytics: this.analyticsEnabled
                });
                
            } catch (error) {
                console.log('Error verificando cookies:', error);
                this.accepted = false;
                this.analyticsEnabled = false;
            }
        },

        getCookie(name) {
            try {
                const value = `; ${document.cookie}`;
                const parts = value.split(`; ${name}=`);
                if (parts.length === 2) return parts.pop().split(';').shift();
            } catch (error) {
                console.log('Error leyendo cookie:', error);
            }
            return null;
        },

        setCookie(name, value, days = 365) {
            try {
                const expires = new Date();
                expires.setTime(expires.getTime() + (days * 24 * 60 * 60 * 1000));
                document.cookie = `${name}=${value};expires=${expires.toUTCString()};path=/;SameSite=Lax`;
                console.log(`Cookie ${name} guardada:`, value);
            } catch (error) {
                console.log('Error guardando cookie:', error);
            }
        },

        openSettings() {
            console.log('Abriendo configuración cookies');
            this.showSettings = true;
        },

        closeSettings() {
            console.log('Cerrando configuración cookies');
            this.showSettings = false;
        },

        acceptAll() {
            console.log('Aceptar todas las cookies');
            this.analyticsEnabled = true;
            this.save('all');
        },

        acceptEssential() {
            console.log('Aceptar solo esenciales');
            this.analyticsEnabled = false;
            this.save('essential');
        },

        saveSettings() {
            console.log('Guardando configuración personalizada');
            this.save('custom');
            this.showSettings = false;
        },

        save(type) {
            console.log('Guardando preferencias:', type);
            
            try {
                // Guardar en cookies
                this.setCookie('cookie-consent', type);
                this.setCookie('cookie-analytics', this.analyticsEnabled);
                this.setCookie('cookie-consent-date', new Date().toISOString());
                
                this.accepted = true;
                
                if (this.analyticsEnabled) {
                    this.loadAnalytics();
                }
                
                console.log('Preferencias guardadas exitosamente');
                
            } catch (error) {
                console.log('Error guardando preferencias:', error);
            }
        },

        loadAnalytics() {
            console.log('📊 Cargando scripts de analytics...');
            // Aquí iría Google Analytics, etc.
        }
    }));

    console.log('🍪 Alpine cookies system loaded');
});