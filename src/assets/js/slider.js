document.addEventListener('DOMContentLoaded', () => {
    const slides = document.querySelectorAll('.slider .slide');
    const prevBtn = document.querySelector('.slider-prev');
    const nextBtn = document.querySelector('.slider-next');

    if (slides.length === 0) return;

    let currentSlide = 0;
    const slideInterval = 5000; // 5 seconds

    function showSlide(index) {
        // Remove 'active-slide' class from all slides
        slides.forEach(slide => {
            slide.classList.remove('active-slide');
        });
        // Add 'active-slide' class to the correct one
        slides[index].classList.add('active-slide');
    }

    function nextSlide() {
        currentSlide = (currentSlide + 1) % slides.length;
        showSlide(currentSlide);
    }

    function prevSlide() {
        currentSlide = (currentSlide - 1 + slides.length) % slides.length;
        showSlide(currentSlide);
    }

    // Event listeners for buttons
    if (nextBtn) {
        nextBtn.addEventListener('click', () => {
            nextSlide();
            // Reset the interval when a button is clicked
            clearInterval(autoSlide);
            autoSlide = setInterval(nextSlide, slideInterval);
        });
    }

    if (prevBtn) {
        prevBtn.addEventListener('click', () => {
            prevSlide();
            // Reset the interval when a button is clicked
            clearInterval(autoSlide);
            autoSlide = setInterval(nextSlide, slideInterval);
        });
    }
    
    // Initial display
    showSlide(currentSlide);

    // Auto-slide functionality
    let autoSlide = setInterval(nextSlide, slideInterval);
});