(function() {
  var poll = setInterval(function() {
    var header = document.querySelector('.edit-post-header');
    if (!header || document.querySelector('.bc-new-post-btn')) return;
    clearInterval(poll);
    var settings = header.querySelector('.edit-post-header__settings');
    var target = settings || header;
    var btn = document.createElement('a');
    btn.className = 'bc-new-post-btn components-button is-secondary';
    btn.href = 'post-new.php';
    btn.title = 'Crear nuevo art\u00edculo';
    btn.style.cssText = 'display:inline-flex;align-items:center;gap:4px;margin-left:8px;height:33px;padding:0 12px;border-radius:3px;font-size:13px;text-decoration:none;white-space:nowrap';
    btn.innerHTML = '<span class="dashicons dashicons-plus-alt2" style="font-size:16px;width:16px;height:16px;"></span> Nuevo Art\u00edculo';
    target.appendChild(btn);
  }, 300);
})();
