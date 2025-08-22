document.addEventListener('DOMContentLoaded', function() {
    const track = document.querySelector('.carousel-track');
    const carousel = document.querySelector('.carousel');
    const slides = Array.from(track.children);
    const nextButton = document.querySelector('.carousel-button.next');
    const prevButton = document.querySelector('.carousel-button.prev');
    
    let isDragging = false;
    let startPos = 0;
    let currentTranslate = 0;
    let prevTranslate = 0;
    let animationID = 0;
    let currentIndex = 0;

    // Disable context menu on long press
    window.oncontextmenu = function(event) {
        if (event.target.closest('.carousel')) {
            event.preventDefault();
            event.stopPropagation();
            return false;
        }
    }

    // Button click handlers
    nextButton.addEventListener('click', () => {
        const maxIndex = slides.length - 1;
        if (currentIndex < maxIndex) {
            currentIndex++;
            setPositionByIndex(true);
        } else {
            // If at the end, smoothly return to start
            currentIndex = 0;
            setPositionByIndex(true);
        }
    });

    prevButton.addEventListener('click', () => {
        if (currentIndex > 0) {
            currentIndex--;
            setPositionByIndex(true);
        } else {
            // If at the start, smoothly go to end
            currentIndex = slides.length - 1;
            setPositionByIndex(true);
        }
    });

    // Touch events
    track.addEventListener('touchstart', touchStart);
    track.addEventListener('touchend', touchEnd);
    track.addEventListener('touchmove', touchMove);

    // Mouse events
    track.addEventListener('mousedown', touchStart);
    track.addEventListener('mouseup', touchEnd);
    track.addEventListener('mouseleave', touchEnd);
    track.addEventListener('mousemove', touchMove);

    function touchStart(event) {
        isDragging = true;
        startPos = getPositionX(event);
        animationID = requestAnimationFrame(animation);
        track.style.cursor = 'grabbing';
    }

    function touchEnd() {
        isDragging = false;
        cancelAnimationFrame(animationID);
        track.style.cursor = 'grab';

        const movedBy = currentTranslate - prevTranslate;

        // Snap to closest slide
        if (Math.abs(movedBy) > 100) {
            if (movedBy < 0 && currentIndex < slides.length - 1) {
                currentIndex++;
            } else if (movedBy > 0 && currentIndex > 0) {
                currentIndex--;
            }
        }

        setPositionByIndex(true);
    }

    function touchMove(event) {
        if (isDragging) {
            const currentPosition = getPositionX(event);
            currentTranslate = prevTranslate + currentPosition - startPos;
        }
    }

    function getPositionX(event) {
        return event.type.includes('mouse') ? event.pageX : event.touches[0].clientX;
    }

    function animation() {
        setSliderPosition();
        if (isDragging) requestAnimationFrame(animation);
    }

    function setPositionByIndex(smooth = false) {
        const slideWidth = slides[0].offsetWidth;
        const gap = 15; // Match the CSS gap value
        const moveAmount = slideWidth * 0.8; // Move by 80% of image width
        
        // Calculate total translation with just left padding
        currentTranslate = -(currentIndex * moveAmount) + 20; // 20px padding from left edge
        
        // Add boundaries to prevent over-scrolling
        const minTranslate = -((slides.length - 1) * moveAmount);
        if (currentTranslate < minTranslate) currentTranslate = minTranslate;
        if (currentTranslate > 20) currentTranslate = 20;
        
        prevTranslate = currentTranslate;
        
        // Add/remove transition based on whether it's a smooth movement
        track.style.transition = smooth ? 'transform 0.3s ease-out' : '';
        setSliderPosition();
        
        // Remove transition after it's done
        if (smooth) {
            setTimeout(() => {
                track.style.transition = '';
            }, 300);
        }
    }

    function setSliderPosition() {
        track.style.transform = `translateX(${currentTranslate}px)`;
    }

    // Window resize
    window.addEventListener('resize', () => setPositionByIndex(true));

    // Initial setup
    setPositionByIndex(true);
});
