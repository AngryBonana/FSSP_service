class CardCarousel {
  constructor() {
    this.optionsContainer = document.querySelector('.options');
    this.originalOptions = Array.from(document.querySelectorAll('.option'));
    this.modalOverlay = document.getElementById('modalOverlay');
    this.modalBody = document.getElementById('modalBody');
    
    // Константы
    this.ANIMATION_DURATION = 800;
    this.SCROLL_DEBOUNCE = 100;
    this.VISIBLE_CARDS = 5;
    this.SWIPE_THRESHOLD = 50;
    
    // Состояние
    this.options = [];
    this.currentIndex = 0;
    this.isAnimating = false;
    this.scrollTimeout = null;
    this.ignoreScrollEvent = false;
    this.touchStartX = 0;
    this.isTouchScrolling = false;
    this.lastScrollTime = 0;
    this.scrollLock = false;
    this.scrollDirection = 0;
  }

  init() {
    this.addLoopIndicator();
    this.cloneCards();
    this.activateCard(this.currentIndex + this.VISIBLE_CARDS);
    this.centerCard(this.currentIndex + this.VISIBLE_CARDS, false);
    this.setupEventListeners();
  }

  addLoopIndicator() {
    const indicator = document.createElement('div');
    indicator.className = 'loop-indicator';
    indicator.title = 'Циклическая навигация включена';
    this.originalOptions[0].appendChild(indicator);
  }

  cloneCards() {
    // Добавляем клоны в начало
    for (let i = 0; i < this.VISIBLE_CARDS; i++) {
      const clone = this.originalOptions[this.originalOptions.length - 1 - i].cloneNode(true);
      clone.classList.remove('active');
      this.optionsContainer.insertBefore(clone, this.optionsContainer.firstChild);
    }
    
    // Добавляем клоны в конец
    for (let i = 0; i < this.VISIBLE_CARDS; i++) {
      const clone = this.originalOptions[i].cloneNode(true);
      clone.classList.remove('active');
      this.optionsContainer.appendChild(clone);
    }
    
    this.options = Array.from(document.querySelectorAll('.option'));
  }

  activateCard(index) {
    this.options.forEach((card, i) => {
      card.classList.toggle('active', i === index);
    });
    this.currentIndex = index - this.VISIBLE_CARDS;
  }

  centerCard(index, smooth = true) {
    if (this.ignoreScrollEvent || !this.options[index]) return;
    
    const card = this.options[index];
    const containerWidth = this.optionsContainer.offsetWidth;
    const cardWidth = card.offsetWidth;
    const scrollPos = card.offsetLeft - (containerWidth / 2) + (cardWidth / 2);
    
    this.optionsContainer.scrollTo({
      left: scrollPos,
      behavior: smooth ? 'smooth' : 'auto'
    });
  }

  navigateToIndex(targetIndex) {
    if (this.isAnimating) return;
    
    this.isAnimating = true;
    let newIndex = targetIndex;
    
    // Циклическая навигация
    if (newIndex < 0) {
      newIndex = this.originalOptions.length - 1;
    } else if (newIndex >= this.originalOptions.length) {
      newIndex = 0;
    }
    
    const displayIndex = newIndex + this.VISIBLE_CARDS;
    this.activateCard(displayIndex);
    this.centerCard(displayIndex, true);
    
    // Коррекция после циклического перехода
    if (targetIndex < 0 || targetIndex >= this.originalOptions.length) {
      setTimeout(() => this.adjustPositionAfterLoop(newIndex), this.ANIMATION_DURATION);
    } else {
      setTimeout(() => { 
        this.isAnimating = false;
        this.scrollLock = false;
      }, this.ANIMATION_DURATION);
    }
  }

  adjustPositionAfterLoop(correctIndex) {
    this.ignoreScrollEvent = true;
    const displayIndex = correctIndex + this.VISIBLE_CARDS;
    this.centerCard(displayIndex, false);
    setTimeout(() => { 
      this.ignoreScrollEvent = false; 
      this.isAnimating = false;
      this.scrollLock = false;
    }, 50);
  }

  findClosestCardIndex() {
    const containerCenter = this.optionsContainer.scrollLeft + (this.optionsContainer.offsetWidth / 2);
    
    return this.options.reduce((closest, card, index) => {
      const cardCenter = card.offsetLeft + (card.offsetWidth / 2);
      const distance = Math.abs(cardCenter - containerCenter);
      return distance < closest.distance ? { index, distance } : closest;
    }, { index: 0, distance: Infinity }).index - this.VISIBLE_CARDS;
  }

  openModal(card) {
    const cardContent = card.querySelector('.card-content').cloneNode(true);
    const cardText = cardContent.querySelector('.card-text');
    
    cardText.style.display = 'block';
    cardText.style.webkitLineClamp = 'unset';
    cardText.style.overflowY = 'auto';
    
    this.modalBody.innerHTML = '';
    this.modalBody.appendChild(cardContent);
    this.modalOverlay.style.display = 'flex';
    document.body.style.overflow = 'hidden';
    
    const closeModal = () => {
      this.modalOverlay.style.display = 'none';
      document.body.style.overflow = '';
      document.removeEventListener('keydown', handleEscape);
    };
    
    const handleEscape = (e) => e.key === 'Escape' && closeModal();
    
    document.querySelector('.modal-close').addEventListener('click', closeModal);
    document.addEventListener('keydown', handleEscape);
    this.modalOverlay.addEventListener('click', (e) => e.target === this.modalOverlay && closeModal());
  }

  handleWheelScroll(e) {
    if (this.isAnimating || this.scrollLock) {
      e.preventDefault();
      return;
    }
    
    const now = Date.now();
    if (now - this.lastScrollTime < 200) {
      e.preventDefault();
      return;
    }
    
    // Определяем направление (приоритет горизонтальному скроллу)
    const delta = Math.abs(e.deltaX) > Math.abs(e.deltaY) ? e.deltaX : e.deltaY;
    this.scrollDirection = Math.sign(delta);
    
    // Блокируем дальнейший скролл до завершения анимации
    this.scrollLock = true;
    e.preventDefault();
    
    // Переходим на следующую/предыдущую карточку
    this.navigateToIndex(this.currentIndex + this.scrollDirection);
    
    this.lastScrollTime = now;
  }

  setupEventListeners() {
    // Клик по карточке
    this.optionsContainer.addEventListener('click', (e) => {
      const clickedCard = e.target.closest('.option');
      if (!clickedCard || this.isAnimating) return;
      
      if (clickedCard.classList.contains('active')) {
        this.openModal(clickedCard);
      } else {
        const clickedIndex = this.options.indexOf(clickedCard) - this.VISIBLE_CARDS;
        if (clickedIndex !== this.currentIndex) {
          this.navigateToIndex(clickedIndex);
        }
      }
    });
    
    // Автоопределение ближайшей карточки при скролле
    this.optionsContainer.addEventListener('scroll', () => {
      if (this.isAnimating || this.ignoreScrollEvent) return;
      
      clearTimeout(this.scrollTimeout);
      this.scrollTimeout = setTimeout(() => {
        const newIndex = this.findClosestCardIndex();
        if (newIndex !== this.currentIndex) {
          this.navigateToIndex(newIndex);
        }
      }, this.SCROLL_DEBOUNCE);
    }, { passive: true });
    
    // Обработка тач-событий
    this.optionsContainer.addEventListener('touchstart', (e) => {
      if (e.touches.length > 1) return;
      this.touchStartX = e.touches[0].clientX;
      this.isTouchScrolling = true;
    }, { passive: true });
    
    this.optionsContainer.addEventListener('touchmove', (e) => {
      if (!this.isTouchScrolling || this.isAnimating || this.scrollLock) return;
      e.preventDefault();
      
      const touchX = e.touches[0].clientX;
      const diffX = this.touchStartX - touchX;
      
      if (Math.abs(diffX) > this.SWIPE_THRESHOLD) {
        this.scrollLock = true;
        this.navigateToIndex(this.currentIndex + Math.sign(diffX));
        this.isTouchScrolling = false;
      }
    }, { passive: false });
    
    this.optionsContainer.addEventListener('touchend', () => {
      this.isTouchScrolling = false;
    }, { passive: true });
    
    // Обработчик колеса мыши/тачпада
    this.optionsContainer.addEventListener('wheel', this.handleWheelScroll.bind(this), { passive: false });
    
    // Ресайз окна
    window.addEventListener('resize', () => {
      if (!this.isAnimating) {
        this.centerCard(this.currentIndex + this.VISIBLE_CARDS, false);
      }
    });
  }
}

// Инициализация после загрузки DOM
document.addEventListener('DOMContentLoaded', () => {
  new CardCarousel().init();
});