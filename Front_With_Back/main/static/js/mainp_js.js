const initOptions = () => {
    const optionsContainer = document.querySelector('.options');
    if (!optionsContainer) {
        console.error('Контейнер карточек (.options) не найден');
        return;
    }

    // Получаем оригинальные карточки
    let originalOptions = Array.from(document.querySelectorAll('.option:not(.clone)'));
    if (originalOptions.length === 0) {
        console.error('Карточки не найдены. Проверьте рендеринг шаблона.');
        return;
    }

    // Настройки
    const VISIBLE_CARDS = Math.min(7, originalOptions.length); // Максимум 7 видимых карточек
    const ANIMATION_DURATION = 800;
    const SCROLL_DEBOUNCE = 100;
    let currentIndex = 0;
    let isAnimating = false;
    let scrollTimeout;
    let ignoreScroll = false;

    // Добавляем метку на первую карточку
    const addLoopIndicator = () => {
        const indicator = document.createElement('div');
        indicator.className = 'loop-indicator';
        indicator.title = 'Циклическая прокрутка включена';
        originalOptions[0].appendChild(indicator);
    };

    // Клонируем карточки для бесшовности
    const cloneCards = () => {
        // Добавляем класс для идентификации клонов
        originalOptions.forEach(card => card.classList.add('original'));

        // Клонируем последние VISIBLE_CARDS карточек в начало
        for (let i = 0; i < VISIBLE_CARDS; i++) {
            const clone = originalOptions[originalOptions.length - 1 - i].cloneNode(true);
            clone.classList.add('clone');
            clone.classList.remove('active');
            optionsContainer.insertBefore(clone, optionsContainer.firstChild);
        }

        // Клонируем первые VISIBLE_CARDS карточек в конец
        for (let i = 0; i < VISIBLE_CARDS; i++) {
            const clone = originalOptions[i].cloneNode(true);
            clone.classList.add('clone');
            clone.classList.remove('active');
            optionsContainer.appendChild(clone);
        }
    };

    // Получаем все карточки (оригиналы + клоны)
    const getAllCards = () => {
        return Array.from(document.querySelectorAll('.option'));
    };

    // Активируем карточку
    const activateCard = (index) => {
        const allCards = getAllCards();
        allCards.forEach((card, i) => {
            card.classList.toggle('active', i === index);
        });
        currentIndex = (index - VISIBLE_CARDS + originalOptions.length) % originalOptions.length;
    };

    // Центрируем карточку
    const centerCard = (index, smooth = true) => {
        if (ignoreScroll) return;
        
        const allCards = getAllCards();
        const card = allCards[index];
        const containerWidth = optionsContainer.offsetWidth;
        const cardWidth = card.offsetWidth;
        const scrollPos = card.offsetLeft - (containerWidth / 2) + (cardWidth / 2);
        
        optionsContainer.scrollTo({
            left: scrollPos,
            behavior: smooth ? 'smooth' : 'auto'
        });
    };

    // Навигация с учетом клонов
    const navigateToIndex = (targetIndex) => {
        if (isAnimating) return;
        
        isAnimating = true;
        
        // Корректируем индекс для оригинальных карточек
        let newIndex = (targetIndex + originalOptions.length) % originalOptions.length;
        
        // Вычисляем индекс с учетом клонов
        const displayIndex = newIndex + VISIBLE_CARDS;
        
        // Активируем и центрируем
        activateCard(displayIndex);
        centerCard(displayIndex, true);
        
        // Если достигли края (клоны), мгновенно переходим к оригиналу
        if (targetIndex < 0 || targetIndex >= originalOptions.length) {
            setTimeout(() => {
                ignoreScroll = true;
                centerCard(newIndex + VISIBLE_CARDS, false);
                setTimeout(() => ignoreScroll = false, 50);
                isAnimating = false;
            }, ANIMATION_DURATION);
        } else {
            setTimeout(() => {
                isAnimating = false;
            }, ANIMATION_DURATION);
        }
    };

    // Находит ближайшую карточку
    const findClosestCard = () => {
        const allCards = getAllCards();
        const containerCenter = optionsContainer.scrollLeft + (optionsContainer.offsetWidth / 2);
        
        let closestIndex = 0;
        let minDistance = Infinity;
        
        allCards.forEach((card, index) => {
            const cardCenter = card.offsetLeft + (card.offsetWidth / 2);
            const distance = Math.abs(cardCenter - containerCenter);
            
            if (distance < minDistance) {
                minDistance = distance;
                closestIndex = index;
            }
        });
        
        return closestIndex - VISIBLE_CARDS;
    };

    // Обработчики событий
    const setupEventListeners = () => {
        // Клик
        optionsContainer.addEventListener('click', (e) => {
            const clickedCard = e.target.closest('.option');
            if (!clickedCard || isAnimating) return;
            
            const allCards = getAllCards();
            const clickedIndex = allCards.indexOf(clickedCard) - VISIBLE_CARDS;
            navigateToIndex(clickedIndex);
        });

        // Скролл
        optionsContainer.addEventListener('scroll', () => {
            if (isAnimating || ignoreScroll) return;
            
            clearTimeout(scrollTimeout);
            scrollTimeout = setTimeout(() => {
                const newIndex = findClosestCard();
                navigateToIndex(newIndex);
            }, SCROLL_DEBOUNCE);
        }, { passive: true });

        // Колесо мыши
        optionsContainer.addEventListener('wheel', (e) => {
            e.preventDefault();
            if (isAnimating) return;
            navigateToIndex(currentIndex + Math.sign(e.deltaY));
        }, { passive: false });

        // Свайпы
        let touchStartX = 0;
        optionsContainer.addEventListener('touchstart', (e) => {
            touchStartX = e.touches[0].clientX;
        }, { passive: true });

        optionsContainer.addEventListener('touchend', (e) => {
            if (isAnimating) return;
            const diffX = touchStartX - e.changedTouches[0].clientX;
            if (Math.abs(diffX) > 50) {
                navigateToIndex(currentIndex + Math.sign(diffX));
            }
        }, { passive: true });
    };

    // Инициализация
    const init = () => {
        addLoopIndicator();
        cloneCards();
        activateCard(VISIBLE_CARDS); // Активная карточка (первая оригинальная)
        centerCard(VISIBLE_CARDS, false);
        setupEventListeners();
        
        // Для дебага
        console.log(`Инициализировано ${originalOptions.length} карточек (${VISIBLE_CARDS} видимых)`);
    };

    init();
};

// Запускаем после загрузки DOM
document.addEventListener('DOMContentLoaded', initOptions);