// Inicialización de Alpine.js para SecureCheck

document.addEventListener('alpine:init', () => {
  // Componente para el formulario de verificación
  Alpine.data('verificationForm', () => ({
    email: '',
    isLoading: false,
    
    submitForm() {
      this.isLoading = true;
      // El resto lo maneja HTMX
    }
  }));
  
  // Componente para el sistema de notificaciones toast
  Alpine.data('toastSystem', () => ({
    toasts: [],
    
    showToast(message, type = 'info', duration = 5000) {
      const id = Date.now();
      this.toasts.push({ id, message, type });
      
      setTimeout(() => {
        this.removeToast(id);
      }, duration);
    },
    
    removeToast(id) {
      this.toasts = this.toasts.filter(toast => toast.id !== id);
    }
  }));
  
  // Componente para el modal de detalles
  Alpine.data('breachModal', () => ({
    isOpen: false,
    content: '',
    
    open(content) {
      this.content = content;
      this.isOpen = true;
    },
    
    close() {
      this.isOpen = false;
    }
  }));
});

// Configuración de HTMX para CSRF
document.addEventListener('DOMContentLoaded', function() {
  // Configurar HTMX para incluir el token CSRF en todas las peticiones POST
  document.body.addEventListener('htmx:configRequest', function(evt) {
    if (evt.detail.verb === 'post') {
      const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
      evt.detail.headers['X-CSRFToken'] = csrfToken;
    }
  });
  
  // Manejar eventos de HTMX
  document.body.addEventListener('htmx:afterSwap', function(evt) {
    // Reinicializar componentes Alpine después de actualizaciones HTMX si es necesario
    if (window.Alpine) {
      window.Alpine.initTree(evt.detail.target);
    }
  });
  
  // Manejar respuestas con errores
  document.body.addEventListener('htmx:responseError', function(evt) {
    console.error('Error en respuesta HTMX:', evt.detail);
    // Mostrar notificación de error
    const toastEvent = new CustomEvent('showToast', {
      detail: {
        message: 'Error en la solicitud: ' + (evt.detail.error || 'Error desconocido'),
        type: 'error'
      }
    });
    window.dispatchEvent(toastEvent);
  });
});
