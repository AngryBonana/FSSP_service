const initOptions = () => {
    const optionsContainer = document.querySelector('.options');
    if (!optionsContainer) return;

    const originalOptions = Array.from(document.querySelectorAll('.option:not(.clone)'));
    if (originalOptions.length === 0) return;

    // Определяем режим работы в зависимости от количества карточек
    const isCompactMode = originalOptions.length < 6;

    if (isCompactMode) {
        initCompactCarousel(originalOptions, optionsContainer);
    } else {
        initExtendedCarousel(originalOptions, optionsContainer);
    }

    // Инициализация модального окна (общая для обоих режимов)
    initModal();
};

// Инициализация модального окна
const initModal = () => {
    const modalOverlay = document.getElementById('modalOverlay');
    const modalBody = document.getElementById('modalBody');

    if (!modalOverlay || !modalBody) return;

    const openModal = (card) => {
        const cardContent = card.querySelector('.card-content').cloneNode(true);
        const cardText = cardContent.querySelector('.card-text');

        if (cardText) {
            cardText.style.display = 'block';
            cardText.style.webkitLineClamp = 'unset';
            cardText.style.overflowY = 'auto';
        }

        modalBody.innerHTML = '';
        modalBody.appendChild(cardContent);
        modalOverlay.style.display = 'flex';
        document.body.style.overflow = 'hidden';
    };

    const closeModal = () => {
        modalOverlay.style.display = 'none';
        document.body.style.overflow = '';
        document.removeEventListener('keydown', handleEscape);
    };

    const handleEscape = (e) => e.key === 'Escape' && closeModal();

    document.querySelector('.modal-close')?.addEventListener('click', closeModal);
    document.addEventListener('keydown', handleEscape);
    modalOverlay.addEventListener('click', (e) => e.target === modalOverlay && closeModal());

    // Добавляем обработчик клика только на активные карточки
    document.addEventListener('click', (e) => {
        const activeCard = e.target.closest('.option.active');
        if (activeCard && !e.target.closest('.modal-content')) {
            openModal(activeCard);
        }
    });
};

// Режим для <6 карточек (компактный)
const initCompactCarousel = (originalOptions, container) => {
    let currentIndex = 0;
    let isAnimating = false;
    const ANIMATION_DURATION = 800;
    let scrollTimeout;

    // Активируем карточку по индексу с анимацией
    const activateCard = (index) => {
        if (isAnimating) return;

        isAnimating = true;
        const prevIndex = currentIndex;
        currentIndex = (index + originalOptions.length) % originalOptions.length;

        // Анимация для предыдущей активной карточки
        if (originalOptions[prevIndex]) {
            originalOptions[prevIndex].classList.remove('active');
            originalOptions[prevIndex].style.flex = '0 0 var(--option-width)';
        }

        // Анимация для новой активной карточки
        originalOptions[currentIndex].classList.add('active');
        originalOptions[currentIndex].style.flex = '0 0 var(--active-width)';

        // Центрируем активную карточку
        centerCard(currentIndex);

        setTimeout(() => isAnimating = false, ANIMATION_DURATION);
    };

    // Центрирование карточки в контейнере
    const centerCard = (index) => {
        const card = originalOptions[index];
        if (!card) return;

        const containerWidth = container.offsetWidth;
        const cardWidth = card.offsetWidth;
        const scrollPos = card.offsetLeft - (containerWidth / 2) + (cardWidth / 2);

        container.scrollTo({
            left: scrollPos,
            behavior: 'smooth'
        });
    };

    // Находим ближайшую карточку к центру
    const findClosestCard = () => {
        const containerCenter = container.scrollLeft + (container.offsetWidth / 2);

        let closestIndex = 0;
        let minDistance = Infinity;

        originalOptions.forEach((card, index) => {
            const cardCenter = card.offsetLeft + (card.offsetWidth / 2);
            const distance = Math.abs(cardCenter - containerCenter);

            if (distance < minDistance) {
                minDistance = distance;
                closestIndex = index;
            }
        });

        return closestIndex;
    };

    // Обработка кликов по карточкам
    const setupCardClickHandlers = () => {
        container.addEventListener('click', (e) => {
            const clickedCard = e.target.closest('.option');
            if (!clickedCard || isAnimating) return;

            const clickedIndex = originalOptions.indexOf(clickedCard);
            if (clickedIndex !== -1 && clickedIndex !== currentIndex) {
                e.stopPropagation(); // Предотвращаем всплытие события
                activateCard(clickedIndex);
            }
        });
    };

    // Обработка скролла
    const setupScrollHandlers = () => {
        container.addEventListener('scroll', () => {
            if (isAnimating) return;

            clearTimeout(scrollTimeout);
            scrollTimeout = setTimeout(() => {
                const newIndex = findClosestCard();
                if (newIndex !== currentIndex) {
                    activateCard(newIndex);
                }
            }, 100);
        }, { passive: true });

        // Обработка колесика мыши/тачпада
        container.addEventListener('wheel', (e) => {
            e.preventDefault();
            if (isAnimating) return;

            if (Math.abs(e.deltaX) > Math.abs(e.deltaY)) {
                activateCard(currentIndex + Math.sign(e.deltaX));
            } else {
                activateCard(currentIndex + Math.sign(e.deltaY));
            }
        }, { passive: false });

        // Обработка тач-событий
        let touchStartX = 0;
        container.addEventListener('touchstart', (e) => {
            touchStartX = e.touches[0].clientX;
        }, { passive: true });

        container.addEventListener('touchend', (e) => {
            if (isAnimating) return;
            const diffX = touchStartX - e.changedTouches[0].clientX;
            if (Math.abs(diffX) > 50) {
                activateCard(currentIndex + Math.sign(diffX));
            }
        }, { passive: true });
    };

    // Инициализация компактного режима
    originalOptions.forEach((card, i) => {
        card.style.flex = i === 0 ? '0 0 var(--active-width)' : '0 0 var(--option-width)';
        card.classList.toggle('active', i === 0);
    });

    setupCardClickHandlers();
    setupScrollHandlers();

    // Центрируем первую карточку
    setTimeout(() => centerCard(0), 100);
};

// Режим для ≥6 карточек (расширенный с клонированием)
const initExtendedCarousel = (originalOptions, container) => {
    const VISIBLE_CARDS = Math.min(7, originalOptions.length);
    const ANIMATION_DURATION = 800;
    let currentIndex = 0;
    let isAnimating = false;
    let ignoreScroll = false;
    let scrollTimeout;

    // Добавляем метку на первую карточку
    const addLoopIndicator = () => {
        const indicator = document.createElement('div');
        indicator.className = 'loop-indicator';
        originalOptions[0].appendChild(indicator);
    };

    // Клонируем карточки для бесшовности
    const cloneCards = () => {
        originalOptions.forEach(card => card.classList.add('original'));

        // Клонируем последние VISIBLE_CARDS карточек в начало
        for (let i = 0; i < VISIBLE_CARDS; i++) {
            const clone = originalOptions[originalOptions.length - 1 - i].cloneNode(true);
            clone.classList.add('clone');
            clone.classList.remove('active');
            container.insertBefore(clone, container.firstChild);
        }

        // Клонируем первые VISIBLE_CARDS карточек в конец
        for (let i = 0; i < VISIBLE_CARDS; i++) {
            const clone = originalOptions[i].cloneNode(true);
            clone.classList.add('clone');
            clone.classList.remove('active');
            container.appendChild(clone);
        }
    };

    const getAllCards = () => Array.from(document.querySelectorAll('.option'));

    const activateCard = (index) => {
        const allCards = getAllCards();
        allCards.forEach((card, i) => {
            card.classList.toggle('active', i === index);
        });
        currentIndex = (index - VISIBLE_CARDS + originalOptions.length) % originalOptions.length;
    };

    const centerCard = (index, smooth = true) => {
        if (ignoreScroll) return;

        const allCards = getAllCards();
        const card = allCards[index];
        const containerWidth = container.offsetWidth;
        const cardWidth = card.offsetWidth;
        const scrollPos = card.offsetLeft - (containerWidth / 2) + (cardWidth / 2);

        container.scrollTo({
            left: scrollPos,
            behavior: smooth ? 'smooth' : 'auto'
        });
    };

    const navigateToIndex = (targetIndex) => {
        if (isAnimating) return;
        isAnimating = true;

        let newIndex = (targetIndex + originalOptions.length) % originalOptions.length;
        const displayIndex = newIndex + VISIBLE_CARDS;

        activateCard(displayIndex);
        centerCard(displayIndex, true);

        if (targetIndex < 0 || targetIndex >= originalOptions.length) {
            setTimeout(() => {
                ignoreScroll = true;
                centerCard(newIndex + VISIBLE_CARDS, false);
                setTimeout(() => ignoreScroll = false, 50);
                isAnimating = false;
            }, ANIMATION_DURATION);
        } else {
            setTimeout(() => isAnimating = false, ANIMATION_DURATION);
        }
    };

    const findClosestCard = () => {
        const allCards = getAllCards();
        const containerCenter = container.scrollLeft + (container.offsetWidth / 2);

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

    const setupEventListeners = () => {
        container.addEventListener('click', (e) => {
            const clickedCard = e.target.closest('.option');
            if (!clickedCard || isAnimating) return;

            const allCards = getAllCards();
            const clickedIndex = allCards.indexOf(clickedCard) - VISIBLE_CARDS;
            if (clickedIndex !== currentIndex) {
                e.stopPropagation(); // Предотвращаем всплытие события
                navigateToIndex(clickedIndex);
            }
        });

        container.addEventListener('scroll', () => {
            if (isAnimating || ignoreScroll) return;

            clearTimeout(scrollTimeout);
            scrollTimeout = setTimeout(() => {
                const newIndex = findClosestCard();
                navigateToIndex(newIndex);
            }, 100);
        }, { passive: true });

        container.addEventListener('wheel', (e) => {
            e.preventDefault();
            if (isAnimating) return;
            navigateToIndex(currentIndex + Math.sign(e.deltaY));
        }, { passive: false });

        let touchStartX = 0;
        container.addEventListener('touchstart', (e) => {
            touchStartX = e.touches[0].clientX;
        }, { passive: true });

        container.addEventListener('touchend', (e) => {
            if (isAnimating) return;
            const diffX = touchStartX - e.changedTouches[0].clientX;
            if (Math.abs(diffX) > 50) {
                navigateToIndex(currentIndex + Math.sign(diffX));
            }
        }, { passive: true });
    };

    // Инициализация расширенного режима
    addLoopIndicator();
    cloneCards();
    activateCard(VISIBLE_CARDS);
    centerCard(VISIBLE_CARDS, false);
    setupEventListeners();
};

document.addEventListener('DOMContentLoaded', initOptions);