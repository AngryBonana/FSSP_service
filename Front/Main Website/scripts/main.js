const initOptions = () => {
  const optionsContainer = document.querySelector('.options');
  const options = document.querySelectorAll('.option');
  let currentIndex = 0;
  let isAnimating = false;
  let scrollTimeout;
  
  // Set CSS variable with total options count
  optionsContainer.style.setProperty('--total-options', options.length);
  
  // Initialize first option as active
  options[0].classList.add('active');
  
  // Click handler
  optionsContainer.addEventListener('click', (event) => {
    const clickedOption = event.target.closest('.option');
    if (!clickedOption || isAnimating) return;
    
    const clickedIndex = Array.from(options).indexOf(clickedOption);
    if (clickedIndex !== currentIndex) {
      navigateToIndex(clickedIndex);
    }
  });
  
  // Improved scroll handler with momentum
  optionsContainer.addEventListener('scroll', () => {
    if (isAnimating) return;
    
    clearTimeout(scrollTimeout);
    scrollTimeout = setTimeout(() => {
      const newIndex = findClosestSnapIndex();
      if (newIndex !== currentIndex) {
        navigateToIndex(newIndex);
      }
    }, 100);
  }, { passive: true });
  
  // Wheel handler for fast scrolling
  optionsContainer.addEventListener('wheel', (e) => {
    if (isAnimating) return;
    
    e.preventDefault();
    const direction = Math.sign(e.deltaY);
    const newIndex = Math.max(0, Math.min(currentIndex + direction, options.length - 1));
    
    if (newIndex !== currentIndex) {
      navigateToIndex(newIndex);
    }
  }, { passive: false });
  
  // Touch handlers for mobile
  let touchStartX = 0;
  
  optionsContainer.addEventListener('touchstart', (e) => {
    touchStartX = e.touches[0].clientX;
  }, { passive: true });
  
  optionsContainer.addEventListener('touchend', (e) => {
    if (isAnimating) return;
    
    const touchEndX = e.changedTouches[0].clientX;
    const diffX = touchEndX - touchStartX;
    
    if (Math.abs(diffX) > 50) {
      const direction = Math.sign(diffX) * -1; // Inverse for natural swipe
      const newIndex = Math.max(0, Math.min(currentIndex + direction, options.length - 1));
      
      if (newIndex !== currentIndex) {
        navigateToIndex(newIndex);
      }
    }
  }, { passive: true });
  
  function findClosestSnapIndex() {
    const containerRect = optionsContainer.getBoundingClientRect();
    const containerCenter = containerRect.left + containerRect.width / 2;
    
    let closestIndex = 0;
    let minDistance = Infinity;
    
    options.forEach((option, index) => {
      const optionRect = option.getBoundingClientRect();
      const optionCenter = optionRect.left + optionRect.width / 2;
      const distance = Math.abs(optionCenter - containerCenter);
      
      if (distance < minDistance) {
        minDistance = distance;
        closestIndex = index;
      }
    });
    
    return closestIndex;
  }
  
  function navigateToIndex(newIndex) {
    isAnimating = true;
    currentIndex = newIndex;
    
    // Update active class
    options.forEach((option, index) => {
      option.classList.toggle('active', index === currentIndex);
    });
    
    // Smooth scroll to the new option
    options[currentIndex].scrollIntoView({
      behavior: 'smooth',
      block: 'nearest',
      inline: 'center'
    });
    
    // Reset animation flag after transition
    setTimeout(() => {
      isAnimating = false;
    }, 400);
  }
};

document.addEventListener('DOMContentLoaded', initOptions);