// Функция установки темы
function setTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
    
    // Меняем все изображения
    document.querySelectorAll('[data-light], [data-dark]').forEach(img => {
        img.src = theme === 'dark' ? img.getAttribute('data-dark') : img.getAttribute('data-light');
    });
}

// Проверяем сохраненную тему при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    const savedTheme = localStorage.getItem('theme') || 'light'; // По умолчанию светлая
    setTheme(savedTheme);
    
    // Обработчик для кнопки смены темы
    const themeToggle = document.querySelector('.btn_theme');
    if (themeToggle) {
        themeToggle.addEventListener('click', function() {
            const currentTheme = document.documentElement.getAttribute('data-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            setTheme(newTheme);
        });
    }
});