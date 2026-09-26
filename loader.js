/**
 * Grinstr Gearmotor Configurator Loader for Tilda
 * Repository: https://github.com/landbool/configurator
 */
(function() {
    const container = document.getElementById('grinstr-configurator-container') || document.currentScript.parentElement;
    if (!container) return;

    // Full-page backdrop for the entire parent website
    let parentBackdrop = document.getElementById('grinstr-parent-backdrop');
    if (!parentBackdrop) {
        parentBackdrop = document.createElement('div');
        parentBackdrop.id = 'grinstr-parent-backdrop';
        parentBackdrop.style.position = 'fixed';
        parentBackdrop.style.inset = '0';
        parentBackdrop.style.backgroundColor = 'rgba(10, 15, 29, 0.75)';
        parentBackdrop.style.backdropFilter = 'blur(4px)';
        parentBackdrop.style.webkitBackdropFilter = 'blur(4px)';
        parentBackdrop.style.zIndex = '999990';
        parentBackdrop.style.opacity = '0';
        parentBackdrop.style.pointerEvents = 'none';
        parentBackdrop.style.transition = 'opacity 0.25s ease';
        document.body.appendChild(parentBackdrop);
    }

    const iframe = document.createElement('iframe');
    iframe.id = 'grinstr-configurator-iframe';
    iframe.src = 'https://landbool.github.io/configurator/index.html?v=' + Date.now();
    iframe.style.width = '100%';
    iframe.style.height = (window.innerWidth < 1024 ? '420px' : '980px');
    iframe.style.border = 'none';
    iframe.style.overflow = 'hidden';
    iframe.style.display = 'block';
    iframe.style.position = 'relative';
    iframe.style.zIndex = '999995';
    iframe.setAttribute('allowtransparency', 'true');

    parentBackdrop.addEventListener('click', function() {
        if (iframe.contentWindow) {
            iframe.contentWindow.postMessage({ type: 'grinstr_close_modals' }, '*');
        }
        parentBackdrop.style.opacity = '0';
        parentBackdrop.style.pointerEvents = 'none';
    });

    // Handle messages from iframe
    window.addEventListener('message', function(e) {
        if (!e.data) return;
        
        if (e.data.type === 'grinstr_scroll_top') {
            const offset = 70;
            const y = iframe.getBoundingClientRect().top + window.pageYOffset - offset;
            window.scrollTo({ top: Math.max(0, y), behavior: 'smooth' });
        }

        // Dynamic iframe height
        if (e.data.type === 'grinstr_resize' && typeof e.data.height === 'number') {
            iframe.style.height = e.data.height + 'px';
        }
        
        // Show whole-site backdrop
        if (e.data.type === 'grinstr_show_backdrop') {
            parentBackdrop.style.pointerEvents = 'auto';
            parentBackdrop.style.opacity = '1';
        }
        
        // Hide whole-site backdrop
        if (e.data.type === 'grinstr_hide_backdrop') {
            parentBackdrop.style.opacity = '0';
            parentBackdrop.style.pointerEvents = 'none';
        }
        
        // Exact user viewport center calculation & backdrop trigger
        if (e.data.type === 'grinstr_request_modal_pos') {
            parentBackdrop.style.pointerEvents = 'auto';
            parentBackdrop.style.opacity = '1';

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
    
    // Fix Tilda top padding on mobile: walk up DOM and zero all padding-top on Tilda wrappers
    if (window.innerWidth < 1024) {
        let el = container;
        while (el && el !== document.body) {
            const cs = getComputedStyle(el);
            const pt = parseInt(cs.paddingTop, 10) || 0;
            const mt = parseInt(cs.marginTop, 10) || 0;
            if (pt > 20) el.style.paddingTop = '0px';
            if (mt > 20) el.style.marginTop = '0px';
            el = el.parentElement;
        }
    }
})();
