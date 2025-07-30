document.addEventListener('DOMContentLoaded', () => {
    // Get all the necessary elements
    const videoCards = document.querySelectorAll('.video-card');
    const videoModal = document.getElementById('video-modal');
    const modalContent = document.querySelector('.modal-content');
    const closeBtn = document.querySelector('.close-modal');
    const videoIframe = document.getElementById('video-iframe');

    // If there's no modal on the page, don't run the script
    if (!videoModal) return;

    videoCards.forEach(card => {
        card.addEventListener('click', () => {
            const videoId = card.getAttribute('data-video-id');
            if (videoId) {
                videoIframe.src = `https://www.youtube.com/embed/${videoId}?autoplay=1`;
                videoModal.style.display = 'flex'; // Show the modal
            }
        });
    });

    // Function to close the modal
    function closeModal() {
        videoModal.style.display = 'none'; // Hide the modal
        videoIframe.src = ''; // Stop the video from playing in the background
    }

    // Close the modal when the 'X' button is clicked
    closeBtn.addEventListener('click', closeModal);

    // Close the modal when clicking on the background overlay
    videoModal.addEventListener('click', (e) => {
        if (e.target === videoModal) {
            closeModal();
        }
    });
});