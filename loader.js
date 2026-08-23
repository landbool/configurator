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

    // Auto-resize & center scrolling on modal open
    window.addEventListener('message', function(e) {
        if (!e.data) return;
        if (e.data.type === 'grinstr_resize' && typeof e.data.height === 'number') {
            iframe.style.height = e.data.height + 'px';
        }
        if (e.data.type === 'grinstr_scroll_to_configurator') {
            iframe.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    });

    container.innerHTML = '';
    container.appendChild(iframe);
})();
