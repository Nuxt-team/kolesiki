// Основной JavaScript файл для магазина Колёсики

document.addEventListener('DOMContentLoaded', function() {
    // Автоматическое скрытие алертов через 5 секунд
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(alert => {
        setTimeout(() => {
            if (alert && alert.parentNode) {
                alert.classList.remove('show');
                setTimeout(() => {
                    alert.remove();
                }, 150);
            }
        }, 5000);
    });

    // Товары загружаются через backend, JavaScript не нужен
    
    // Обработчики форм
    setupFormHandlers();
});

// Загрузка товаров - НЕ ИСПОЛЬЗУЕТСЯ, товары отображаются через backend
function loadProducts() {
    // Эта функция больше не нужна, товары загружаются серверным рендерингом
    console.log('Товары загружаются через backend');
}

// Покупка товара теперь происходит через HTML формы, а не через JavaScript
// Эти функции больше не используются, но оставлены для совместимости

function createProductCard(product) {
    console.log('createProductCard deprecated - товары создаются через backend');
}

function buyProduct(productId) {
    console.log('buyProduct deprecated - покупка происходит через HTML формы');
}

// Проверка авторизации пользователя
function isLoggedIn() {
    // Проверяем есть ли ссылка на профиль (означает что пользователь залогинен)
    return document.querySelector('a[href*="/users/profile"]') !== null;
}

// Показ алерта
function showAlert(type, message) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const main = document.querySelector('main.container');
    main.insertBefore(alertDiv, main.firstChild);
    
    // Автоматическое скрытие через 5 секунд
    setTimeout(() => {
        if (alertDiv && alertDiv.parentNode) {
            alertDiv.classList.remove('show');
            setTimeout(() => alertDiv.remove(), 150);
        }
    }, 5000);
}

// Настройка обработчиков форм
function setupFormHandlers() {
    // Добавление индикатора загрузки к формам
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn && !submitBtn.dataset.originalText) {
                // Сохраняем оригинальный текст кнопки
                submitBtn.dataset.originalText = submitBtn.innerHTML;
                
                submitBtn.disabled = true;
                submitBtn.innerHTML = `
                    <span class="spinner-border spinner-border-sm me-2"></span>
                    Обработка...
                `;
                
                // Возвращаем кнопку в исходное состояние через 10 секунд
                setTimeout(() => {
                    if (submitBtn) {
                        submitBtn.disabled = false;
                        submitBtn.innerHTML = submitBtn.dataset.originalText;
                    }
                }, 10000);
            }
        });
    });
}

// Экранирование HTML
function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, function(m) { return map[m]; });
}