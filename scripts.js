// scripts for index.html egyptian gallery

// this script is automatically included by the builder
// additional functionality can be added here
// the main functionality is in the index.html file

document.addEventListener('DOMContentLoaded', function() {
    // additional functionality beyond what's in the embedded script
    
    // enable fullscreen mode
    const imageContainer = document.querySelector('.image-container');
    if (imageContainer) {
        imageContainer.addEventListener('dblclick', function() {
            if (!document.fullscreenElement) {
                document.documentElement.requestFullscreen().catch(err => {
                    console.log(`error attempting to enable fullscreen: ${err.message}`);
                });
            } else {
                if (document.exitFullscreen) {
                    document.exitFullscreen();
                }
            }
        });
    }
    
    // handle window resize
    window.addEventListener('resize', function() {
        // adjust layout if needed for responsive design
        const infoPanel = document.querySelector('.info-panel');
        if (window.innerWidth < 768) {
            infoPanel.style.flexDirection = 'column';
        } else {
            infoPanel.style.flexDirection = 'row';
        }
    });
    
    // trigger resize event to set initial layout
    window.dispatchEvent(new Event('resize'));
});