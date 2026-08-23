/**
 * Grinstr Gearmotor Configurator Loader for Tilda
 * Repository: https://github.com/landbool/configurator
 */
(function() {
    const container = document.getElementById('grinstr-configurator-container') || document.currentScript.parentElement;
    if (!container) return;

    const iframe = document.createElement('iframe');
    iframe.id = 'grinstr-configurator-iframe';
    iframe.src = 'https://landbool.github.io/configurator/index.html?v=' + Date.now();
    iframe.style.width = '100%';
    iframe.style.height = '980px';
    iframe.style.border = 'none';
    iframe.style.overflow = 'hidden';
    iframe.style.display = 'block';
    iframe.setAttribute('allowtransparency', 'true');

    // Auto-resize & exact viewport modal positioning (without any page scroll jump)
    window.addEventListener('message', function(e) {
        if (!e.data) return;
        
        // Dynamic iframe height
        if (e.data.type === 'grinstr_resize' && typeof e.data.height === 'number') {
            iframe.style.height = e.data.height + 'px';
        }
        
        // Exact user viewport center calculation
        if (e.data.type === 'grinstr_request_modal_pos') {
            const rect = iframe.getBoundingClientRect();
            const viewportH = window.innerHeight || document.documentElement.clientHeight;
            
            // Calculate center of user's screen relative to iframe top
            let centerY = -rect.top + (viewportH / 2);
            
            // Clamp within iframe boundaries
            const modalHalfH = 260;
            const minY = modalHalfH + 15;
            const maxY = (iframe.offsetHeight || 980) - modalHalfH - 15;
            centerY = Math.max(minY, Math.min(maxY, centerY));
            
            if (iframe.contentWindow) {
                iframe.contentWindow.postMessage({ 
                    type: 'grinstr_set_modal_pos', 
                    targetY: Math.round(centerY) 
                }, '*');
            }
        }
    });

    container.innerHTML = '';
    container.appendChild(iframe);
})();
