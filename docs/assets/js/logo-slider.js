document.addEventListener('DOMContentLoaded', () => {
    const sliderContainer = document.querySelector('.logo-slider-container');
    // If the slider doesn't exist on this page, don't run the script
    if (!sliderContainer) {
        return;
    }

    const track = document.querySelector('.logo-slider-track');
    const slides = document.querySelectorAll('.logo-slide');
    const prevBtn = document.querySelector('.logo-slider-prev');
    const nextBtn = document.querySelector('.logo-slider-next');

    // Since we duplicated the slides for a seamless loop, we only count the first half
    const realSlidesCount = slides.length / 2;
    const slideWidth = slides[0].offsetWidth;
    const animationSpeed = 30000; // Speed for the continuous scroll animation (in milliseconds)
    const transitionTime = 0.5; // CSS transition time in seconds

    // Set the total width of the track
    track.style.width = `${slideWidth * slides.length}px`;

    // Clone slides for infinite effect - this is now handled by the Jinja2 template
    // track.style.animation = `scroll ${animationSpeed / 1000}s linear infinite`;

    let currentPosition = 0;
    let slideInterval;

    function updatePosition() {
        track.style.transition = `transform ${transitionTime}s ease-in-out`;
        track.style.transform = `translateX(-${currentPosition * slideWidth}px)`;
    }

    function nextSlide() {
        currentPosition++;
        // When we reach the end of the "fake" slides, silently jump back to the start
        if (currentPosition >= realSlidesCount) {
            updatePosition();
            // Give the CSS transition time to finish before jumping
            setTimeout(() => {
                track.style.transition = 'none'; // Disable transition for the jump
                currentPosition = 0;
                track.style.transform = `translateX(0px)`;
            }, transitionTime * 1000);
        } else {
            updatePosition();
        }
    }
    
    function prevSlide() {
        if (currentPosition <= 0) {
            // Instantly jump to the end of the "fake" list
            track.style.transition = 'none';
            currentPosition = realSlidesCount;
            track.style.transform = `translateX(-${currentPosition * slideWidth}px)`;

            // A tiny delay to allow the browser to process the jump, then transition back
            setTimeout(() => {
                currentPosition--;
                updatePosition();
            }, 50);

        } else {
            currentPosition--;
            updatePosition();
        }
    }
    
    // --- Event Listeners ---
    nextBtn.addEventListener('click', () => {
        nextSlide();
        clearInterval(slideInterval);
        slideInterval = setInterval(nextSlide, 3000);
    });

    prevBtn.addEventListener('click', () => {
        prevSlide();
        clearInterval(slideInterval);
        slideInterval = setInterval(nextSlide, 3000);
    });
    
    // Pause on hover
    sliderContainer.addEventListener('mouseenter', () => clearInterval(slideInterval));
    sliderContainer.addEventListener('mouseleave', () => {
        slideInterval = setInterval(nextSlide, 3000);
    });

    // Start the automatic slide
    slideInterval = setInterval(nextSlide, 3000);
});