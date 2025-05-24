const initOptions = () => {
  const optionsContainer = document.querySelector('.options');
  const originalOptions = Array.from(document.querySelectorAll('.option'));
  const ANIMATION_DURATION = 800;
  const SCROLL_DEBOUNCE = 100;
  const VISIBLE_CARDS = 5; // Количество видимых карточек по бокам
  
  let options = [...originalOptions];
  let currentIndex = 0; // Начинаем с первой оригинальной карточки
  let isAnimating = false;
  let scrollTimeout;
  let ignoreScrollEvent = false;

  const init = () => {
    addLoopIndicator();
    cloneCards();
    activateCard(currentIndex + VISIBLE_CARDS); // Активная карточка с учетом клонов
    centerCard(currentIndex + VISIBLE_CARDS, false);
    setupEventListeners();
  };

  const addLoopIndicator = () => {
    const indicator = document.createElement('div');
    indicator.className = 'loop-indicator';
    indicator.title = 'Циклическая навигация включена';
    originalOptions[0].appendChild(indicator);
  };

  const cloneCards = () => {
    // Клонируем карточки для бесшовного перехода
    // Добавляем клоны последних карточек в начало
    for (let i = 0; i < VISIBLE_CARDS; i++) {
      const clone = originalOptions[originalOptions.length - 1 - i].cloneNode(true);
      clone.classList.remove('active');
      optionsContainer.insertBefore(clone, optionsContainer.firstChild);
    }
    
    // Добавляем клоны первых карточек в конец
    for (let i = 0; i < VISIBLE_CARDS; i++) {
      const clone = originalOptions[i].cloneNode(true);
      clone.classList.remove('active');
      optionsContainer.appendChild(clone);
    }
    
    options = Array.from(document.querySelectorAll('.option'));
  };

  const activateCard = (index) => {
    options.forEach((card, i) => {
      card.classList.toggle('active', i === index);
    });
    currentIndex = index - VISIBLE_CARDS; // Храним индекс оригинальной карточки
  };

  const centerCard = (index, smooth = true) => {
    if (ignoreScrollEvent) return;
    
    const card = options[index];
    const containerWidth = optionsContainer.offsetWidth;
    const cardWidth = card.offsetWidth;
    const scrollPos = card.offsetLeft - (containerWidth / 2) + (cardWidth / 2);
    
    optionsContainer.scrollTo({
      left: scrollPos,
      behavior: smooth ? 'smooth' : 'auto'
    });
  };

  const navigateToIndex = (targetIndex) => {
    if (isAnimating) return;
    
    isAnimating = true;
    const prevIndex = currentIndex;
    
    // Коррекция индекса для циклической навигации
    let newIndex = targetIndex;
    if (newIndex < 0) {
      newIndex = originalOptions.length - 1;
    } else if (newIndex >= originalOptions.length) {
      newIndex = 0;
    }
    
    // Вычисляем индекс с учетом клонов
    const displayIndex = newIndex + VISIBLE_CARDS;
    
    // Активируем новую карточку
    activateCard(displayIndex);
    
    // Плавный скролл
    centerCard(displayIndex, true);
    
    // Если это циклический переход, мгновенно корректируем позицию после анимации
    if (targetIndex < 0 || targetIndex >= originalOptions.length) {
      setTimeout(() => {
        adjustPositionAfterLoop(newIndex);
      }, ANIMATION_DURATION);
    } else {
      setTimeout(() => {
        isAnimating = false;
      }, ANIMATION_DURATION);
    }
  };

  const adjustPositionAfterLoop = (correctIndex) => {
    ignoreScrollEvent = true;
    
    // Мгновенно переходим к оригинальной позиции
    const displayIndex = correctIndex + VISIBLE_CARDS;
    centerCard(displayIndex, false);
    
    setTimeout(() => {
      ignoreScrollEvent = false;
      isAnimating = false;
    }, 50);
  };

  const findClosestCardIndex = () => {
    const containerCenter = optionsContainer.scrollLeft + (optionsContainer.offsetWidth / 2);
    let closestIndex = 0;
    let minDistance = Infinity;
    
    options.forEach((card, index) => {
      const cardCenter = card.offsetLeft + (card.offsetWidth / 2);
      const distance = Math.abs(cardCenter - containerCenter);
      
      if (distance < minDistance) {
        minDistance = distance;
        closestIndex = index;
      }
    });
    
    // Возвращаем индекс оригинальной карточки
    return closestIndex - VISIBLE_CARDS;
  };

  const setupEventListeners = () => {
    optionsContainer.addEventListener('click', (e) => {
      const clickedCard = e.target.closest('.option');
      if (!clickedCard || isAnimating) return;
      
      const clickedIndex = options.indexOf(clickedCard) - VISIBLE_CARDS;
      if (clickedIndex !== currentIndex) {
        navigateToIndex(clickedIndex);
      }
    });
    
    optionsContainer.addEventListener('scroll', () => {
      if (isAnimating || ignoreScrollEvent) return;
      
      clearTimeout(scrollTimeout);
      scrollTimeout = setTimeout(() => {
        const newIndex = findClosestCardIndex();
        if (newIndex !== currentIndex) {
          navigateToIndex(newIndex);
        }
      }, SCROLL_DEBOUNCE);
    }, { passive: true });
    
    optionsContainer.addEventListener('wheel', (e) => {
      e.preventDefault();
      if (isAnimating) return;
      
      const direction = Math.sign(e.deltaY);
      navigateToIndex(currentIndex + direction);
    }, { passive: false });
    
    window.addEventListener('resize', () => {
      if (!isAnimating) {
        centerCard(currentIndex + VISIBLE_CARDS, false);
      }
    });
  };

  init();
};

document.addEventListener('DOMContentLoaded', initOptions);