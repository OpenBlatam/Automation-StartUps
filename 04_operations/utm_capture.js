/**
 * utm_capture.js
 * Captura UTMs desde URL, guarda first/last touch en localStorage
 * y autocompleta formularios con campos ocultos.
 * 
 * Uso: <script src="utm_capture.js"></script> antes de </body>
 */

(function () {
  'use strict';

  // Configuración
  const STORAGE_KEYS = {
    LAST: 'utm_last',
    FIRST: 'utm_first',
    LAST_UPDATED: 'utm_last_updated_at'
  };

  // Helper: parsear query string
  const params = new URLSearchParams(window.location.search);
  const get = k => (params.get(k) || '').trim().toLowerCase();

  // Extraer UTMs de la URL actual
  const utm = {
    source: get('utm_source') || 'direct',
    medium: get('utm_medium') || 'none',
    campaign: get('utm_campaign') || '',
    content: get('utm_content') || '',
    term: get('utm_term') || '',
    landing_url: window.location.href.split('#')[0],
    referrer_url: document.referrer || ''
  };

  // Timestamp ISO
  const nowISO = new Date().toISOString();

  // Función: guardar en localStorage
  function saveToStorage(key, data) {
    try {
      localStorage.setItem(key, JSON.stringify({ ...data, ts: nowISO }));
    } catch (e) {
      console.warn('localStorage no disponible:', e);
    }
  }

  // Función: leer de localStorage
  function loadFromStorage(key) {
    try {
      const item = localStorage.getItem(key);
      return item ? JSON.parse(item) : null;
    } catch (e) {
      return null;
    }
  }

  // Guardar last touch (siempre)
  if (utm.source !== 'direct' || utm.campaign) {
    saveToStorage(STORAGE_KEYS.LAST, utm);
    saveToStorage(STORAGE_KEYS.LAST_UPDATED, { timestamp: nowISO });
  }

  // Guardar first touch (solo si no existe)
  const firstTouch = loadFromStorage(STORAGE_KEYS.FIRST);
  if (!firstTouch && (utm.source !== 'direct' || utm.campaign)) {
    saveToStorage(STORAGE_KEYS.FIRST, utm);
  }

  // Función: rellenar inputs por nombre o data-attr
  function fillInputs(scope = document) {
    const last = loadFromStorage(STORAGE_KEYS.LAST) || {};
    const first = loadFromStorage(STORAGE_KEYS.FIRST) || {};

    // Mapeo de campos
    const fieldMap = {
      'utm_source': last.source || '',
      'utm_medium': last.medium || '',
      'utm_campaign': last.campaign || '',
      'utm_content': last.content || '',
      'utm_term': last.term || '',
      'landing_url': last.landing_url || '',
      'referrer_url': last.referrer_url || '',
      'first_utm_source': first.source || '',
      'first_utm_medium': first.medium || '',
      'first_utm_campaign': first.campaign || '',
      'first_utm_content': first.content || '',
      'first_utm_term': first.term || ''
    };

    // Rellenar inputs por name="..."
    Object.entries(fieldMap).forEach(([name, value]) => {
      if (!value) return;
      
      const byName = scope.querySelectorAll(`[name="${name}"]`);
      byName.forEach(el => {
        if ('value' in el) el.value = value;
      });

      // Rellenar por data-utm="..."
      const byData = scope.querySelectorAll(`[data-utm="${name}"]`);
      byData.forEach(el => {
        if ('value' in el) el.value = value;
      });
    });
  }

  // Ejecutar cuando DOM esté listo
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => fillInputs());
  } else {
    fillInputs();
  }

  // Observer para formularios inyectados dinámicamente
  const observer = new MutationObserver(mutations => {
    mutations.forEach(mutation => {
      mutation.addedNodes.forEach(node => {
        if (node.nodeType === 1) {
          fillInputs(node);
        }
      });
    });
  });

  observer.observe(document.documentElement, {
    childList: true,
    subtree: true
  });

  // Opcional: Añadir UTMs a links externos (toggle en false por defecto)
  const APPEND_TO_LINKS = false;

  if (APPEND_TO_LINKS && (utm.source !== 'direct' || utm.campaign)) {
    document.addEventListener('click', e => {
      const link = e.target.closest('a[href]');
      if (!link) return;

      try {
        const url = new URL(link.href, window.location.origin);
        
        // Solo aplicar a links externos (opcional)
        if (url.origin === window.location.origin) return;

        // Añadir UTMs si no existen
        ['utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term'].forEach(key => {
          const value = utm[key.replace('utm_', '')] || '';
          if (value && !url.searchParams.get(key)) {
            url.searchParams.set(key, value);
          }
        });

        link.href = url.toString();
      } catch (err) {
        console.warn('Error procesando link:', err);
      }
    });
  }

  // Exponer funciones útiles al global scope (opcional)
  window.UTMCapture = {
    getLast: () => loadFromStorage(STORAGE_KEYS.LAST),
    getFirst: () => loadFromStorage(STORAGE_KEYS.FIRST),
    fillInputs: (scope) => fillInputs(scope || document),
    clearAll: () => {
      Object.values(STORAGE_KEYS).forEach(key => localStorage.removeItem(key));
    }
  };

})();


