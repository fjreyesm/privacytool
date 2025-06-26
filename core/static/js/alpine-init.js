// static/js/alpine-init.js

document.addEventListener('alpine:init', () => {

    Alpine.data('secureCookies', () => ({
        accepted: true,  // 🔧 FIXED: Siempre true
        showSettings: false,
        analyticsEnabled: false,

        init() {
            console.log('🍪 Cookie system initialized - BANNER DISABLED');
            
            // FORZAR ESTADO ACEPTADO INMEDIATAMENTE
            this.accepted = true;
            this.showSettings = false;
            
            // MARCAR COOKIES COMO ACEPTADAS PARA SIEMPRE
            this.setCookie('cookie-consent', 'essential');
            this.setCookie('cookie-analytics', 'false');
            this.setCookie('cookie-consent-date', new Date().toISOString());
            
            console.log('✅ Banner cookies DESACTIVADO PERMANENTEMENTE');
        },

        checkCookieConsent() {
            // SIEMPRE DEVOLVER ACEPTADO
            this.accepted = true;
            this.analyticsEnabled = false;
            console.log('Cookie consent: ALWAYS ACCEPTED');
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
            console.log('Configuración cookies (DESHABILITADA)');
            // NO HACER NADA - Banner deshabilitado
        },

        closeSettings() {
            console.log('Cerrando configuración cookies');
            this.showSettings = false;
        },

        acceptAll() {
            console.log('Banner deshabilitado - No action needed');
        },

        acceptEssential() {
            console.log('Banner deshabilitado - No action needed');
        },

        saveSettings() {
            console.log('Banner deshabilitado - No action needed');
            this.showSettings = false;
        },

        save(type) {
            // NO HACER NADA - Ya está aceptado
            console.log('Cookies already accepted by default');
        },

        loadAnalytics() {
            console.log('📊 Analytics disabled by default');
            // No cargar analytics por defecto
        }
    }));

    console.log('🍪 Alpine cookies system loaded - BANNER PERMANENTLY DISABLED');
});