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
    iframe.style.height = '1050px';
    iframe.style.border = 'none';
    iframe.style.overflow = 'hidden';
    iframe.style.display = 'block';
    iframe.setAttribute('allowtransparency', 'true');

    // Auto-resize & smooth scroll on message from iframe
    window.addEventListener('message', function(e) {
        if (!e.data) return;
        if (e.data.type === 'grinstr_resize' && e.data.height) {
            iframe.style.height = (e.data.height + 20) + 'px';
        }
        if (e.data.type === 'grinstr_scroll_to_configurator') {
            const rect = iframe.getBoundingClientRect();
            if (rect.top < 0 || rect.top > 200) {
                iframe.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        }
    });

    container.innerHTML = '';
    container.appendChild(iframe);
})();
