document.addEventListener('DOMContentLoaded', function() {
    const menuToggle = document.querySelector('.menu-toggle');
    const sidebar = document.querySelector('.sidebar');
    const mainContent = document.querySelector('.main-content');
    let isSidebarVisible = true;

    // Function to handle menu toggle
    function toggleMenu() {
        isSidebarVisible = !isSidebarVisible;
        sidebar.classList.toggle('collapsed');
        mainContent.classList.toggle('expanded');
        menuToggle.classList.toggle('active');

        // On mobile, use 'active' class instead
        if (window.innerWidth <= 992) {
            sidebar.classList.remove('collapsed');
            sidebar.classList.toggle('active');
        }
    }

    // Toggle menu when button is clicked
    menuToggle.addEventListener('click', function(e) {
        e.stopPropagation();
        toggleMenu();
    });

    // Close menu when clicking outside on mobile
    document.addEventListener('click', function(e) {
        if (window.innerWidth <= 992 && 
            !sidebar.contains(e.target) && 
            !menuToggle.contains(e.target) && 
            sidebar.classList.contains('active')) {
            toggleMenu();
        }
    });

    // Handle window resize
    let resizeTimer;
    window.addEventListener('resize', function() {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(function() {
            if (window.innerWidth > 992) {
                sidebar.classList.remove('active');
                if (!isSidebarVisible) {
                    sidebar.classList.add('collapsed');
                    mainContent.classList.add('expanded');
                }
            } else {
                sidebar.classList.remove('collapsed');
                mainContent.classList.remove('expanded');
                if (!isSidebarVisible) {
                    sidebar.classList.add('active');
                }
            }
        }, 250);
    });
}); 