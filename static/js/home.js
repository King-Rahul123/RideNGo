// home.js — safe, DOM-ready slider + UI handlers
document.addEventListener('DOMContentLoaded', () => {
  // set current year
  const yearEl = document.getElementById('year');
  if (yearEl) yearEl.textContent = new Date().getFullYear();


  // complaint form handler (selector matches your template)
  const complaintForm = document.querySelector('.complaint-form');
  if (complaintForm) {
    complaintForm.addEventListener('submit', function(e){
      e.preventDefault();
      alert('Thanks! Your feedback has been submitted.');
      this.reset();
    });
  }

  /// Slider sync JS — 16s full cycle for 5 slides (3.2s per slide)
  const slidesEl = document.querySelector('.slides');
  const slideEls = Array.from(document.querySelectorAll('.slides .slide'));
  const dots = Array.from(document.querySelectorAll('.dot'));
  const imageSlider = document.querySelector('.image-slider');

  if (!slidesEl || slideEls.length === 0 || dots.length === 0) return;

  const total = slideEls.length;             // 5
  const FULL_CYCLE_MS = 16000;               // 16s
  const PER_SLIDE_MS = Math.round(FULL_CYCLE_MS / total); // 3200ms
  const TRANSITION_MS = 600;                 // should match CSS transition

  let currentIndex = 0;
  let autoplayTimer = null;
  let resumeTimer = null;

  // Ensure widths are correct (defensive)
  slidesEl.style.width = (100 * total) + '%';
  slideEls.forEach(sl => sl.style.width = (100 / total) + '%');

  function setActiveDot(index) {
    dots.forEach((d, i) => {
      d.classList.toggle('active', i === index);
    });
  }

  function showSlide(index) {
    index = ((index % total) + total) % total;
    const movePercent = (index * -100) / total; // e.g. index 1 => -20%
    slidesEl.style.transition = `transform ${TRANSITION_MS}ms ease`;
    slidesEl.style.transform = `translateX(${movePercent}%)`;
    currentIndex = index;
    setActiveDot(index);
  }

  function startAutoplay() {
    stopAutoplay();
    autoplayTimer = setInterval(() => {
      showSlide(currentIndex + 1);
    }, PER_SLIDE_MS);
  }
  function stopAutoplay() {
    if (autoplayTimer) { clearInterval(autoplayTimer); autoplayTimer = null; }
  }

  // Dot interactions (hover to preview, click to jump)
  dots.forEach((dot, idx) => {
    dot.addEventListener('mouseenter', () => {
      stopAutoplay();
      if (resumeTimer) { clearTimeout(resumeTimer); resumeTimer = null; }
      showSlide(idx);
    });
    dot.addEventListener('mouseleave', () => {
      resumeTimer = setTimeout(() => startAutoplay(), 600);
    });
    dot.addEventListener('click', () => {
      showSlide(idx);
      // restart autoplay counting from this slide
      startAutoplay();
    });
  });

  // Pause when hovering images
  if (imageSlider) {
    imageSlider.addEventListener('mouseenter', () => {
      stopAutoplay();
    });
    imageSlider.addEventListener('mouseleave', () => {
      resumeTimer = setTimeout(() => startAutoplay(), 400);
    });
  }

  // Init
  showSlide(0);
  startAutoplay();

  // Keep sizes correct on resize and maintain current slide
  window.addEventListener('resize', () => {
    slidesEl.style.width = (100 * total) + '%';
    slideEls.forEach(sl => sl.style.width = (100 / total) + '%');
    const movePercent = (currentIndex * -100) / total;
    slidesEl.style.transition = 'none';
    slidesEl.style.transform = `translateX(${movePercent}%)`;
    setTimeout(() => slidesEl.style.transition = `transform ${TRANSITION_MS}ms ease`, 50);
  });
});
