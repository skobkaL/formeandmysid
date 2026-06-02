// Минимальный JS для улучшений
document.addEventListener('DOMContentLoaded', function() {
    // Автофокус на полях поиска
    const searchInput = document.querySelector('input[name="q"]');
    if (searchInput && !searchInput.value) {
        searchInput.focus();
    }
    
    // Подтверждение важных действий
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function(e) {
            if (this.dataset.confirm && !confirm(this.dataset.confirm)) {
                e.preventDefault();
            }
        });
    });
});