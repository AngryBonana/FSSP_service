class CardCarousel {
  constructor() {
    this.optionsContainer = document.querySelector('.options');
    this.options = Array.from(document.querySelectorAll('.option'));
    this.prevBtn = document.getElementById('prevBtn');
    this.nextBtn = document.getElementById('nextBtn');
    this.modalOverlay = document.getElementById('modalOverlay');
    this.modalBody = document.getElementById('modalBody');
    
    this.currentIndex = 0;
    this.isAnimating = false;
    this.scrollLock = false;
    this.lastScrollTime = 0;
  }

  init() {
    this.setupEventListeners();
    this.activateCard(this.currentIndex);
  }

  activateCard(index) {
    if (this.isAnimating) return;
    
    this.isAnimating = true;
    this.currentIndex = index;
    
    this.options.forEach((option, i) => {
      option.classList.toggle('active', i === index);
    });
    
    setTimeout(() => {
      this.isAnimating = false;
      this.scrollLock = false;
    }, 1250);
  }

  openModal(card) {
    const cardContent = card.querySelector('.card-content').cloneNode(true);
    const cardText = cardContent.querySelector('.card-text');
    
    if (cardText) {
      cardText.style.display = 'block';
      cardText.style.webkitLineClamp = 'unset';
      cardText.style.overflowY = 'auto';
    }
    
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

  navigate(direction) {
    if (this.scrollLock) return;
    
    let newIndex = this.currentIndex + direction;
    
    if (newIndex < 0) {
      newIndex = this.options.length - 1;
    } else if (newIndex >= this.options.length) {
      newIndex = 0;
    }
    
    this.scrollLock = true;
    this.activateCard(newIndex);
  }

  handleScroll(e) {
    if (this.isAnimating || this.scrollLock) {
      e.preventDefault();
      return;
    }
    
    const now = Date.now();
    if (now - this.lastScrollTime < 200) {
      e.preventDefault();
      return;
    }
    
    const deltaX = Math.abs(e.deltaX);
    const deltaY = Math.abs(e.deltaY);
    
    if (deltaX > deltaY) {
      const direction = Math.sign(e.deltaX);
      this.navigate(-direction);
      e.preventDefault();
    } else if (deltaY > deltaX) {
      const direction = Math.sign(e.deltaY);
      this.navigate(direction);
      e.preventDefault();
    }
    
    this.lastScrollTime = now;
  }

  setupEventListeners() {
    this.optionsContainer.addEventListener('click', (e) => {
      const clickedOption = e.target.closest('.option');
      if (!clickedOption || this.isAnimating) return;
      
      if (clickedOption.classList.contains('active')) {
        this.openModal(clickedOption);
      } else {
        const clickedIndex = this.options.indexOf(clickedOption);
        if (clickedIndex !== this.currentIndex) {
          this.activateCard(clickedIndex);
        }
      }
    });
    
    this.optionsContainer.addEventListener('wheel', this.handleScroll.bind(this), { passive: false });
  
    document.addEventListener('keydown', (e) => {
      if (this.isAnimating) return;
      
      if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') {
        this.navigate(-1);
      } else if (e.key === 'ArrowRight' || e.key === 'ArrowDown') {
        this.navigate(1);
      }
    });
  }
}

document.addEventListener('DOMContentLoaded', () => {
  new CardCarousel().init();
});