// Mobile menu functionality - improved and more reliable
function initMobileMenu() {
    const mobileMenuButton = document.getElementById('mobile-menu-button');
    const mobileMenu = document.getElementById('mobile-menu');
    
    if (!mobileMenuButton || !mobileMenu) {
        console.log('Mobile menu elements not found');
        return;
    }

    console.log('Mobile menu elements found, initializing...');

    // Toggle function
    function toggleMobileMenu() {
        console.log('Toggle mobile menu clicked');
        const isHidden = mobileMenu.classList.contains('hidden');
        
        if (isHidden) {
            // Show menu
            mobileMenu.classList.remove('hidden');
            mobileMenuButton.setAttribute('aria-expanded', 'true');
            document.body.style.overflow = 'hidden';
            document.body.classList.add('menu-open');
            
            // Change icon to X
            const icon = mobileMenuButton.querySelector('svg');
            if (icon) {
                icon.innerHTML = '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>';
            }
            console.log('Mobile menu opened');
        } else {
            // Hide menu
            mobileMenu.classList.add('hidden');
            mobileMenuButton.setAttribute('aria-expanded', 'false');
            document.body.style.overflow = '';
            document.body.classList.remove('menu-open');
            
            // Change icon to hamburger
            const icon = mobileMenuButton.querySelector('svg');
            if (icon) {
                icon.innerHTML = '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16m-7 6h7"></path>';
            }
            console.log('Mobile menu closed');
        }
    }

    // Close menu function
    function closeMobileMenu() {
        mobileMenu.classList.add('hidden');
        mobileMenuButton.setAttribute('aria-expanded', 'false');
        document.body.style.overflow = '';
        document.body.classList.remove('menu-open');
        
        const icon = mobileMenuButton.querySelector('svg');
        if (icon) {
            icon.innerHTML = '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16m-7 6h7"></path>';
        }
        console.log('Mobile menu closed via close function');
    }

    // Remove any existing event listeners by cloning the button
    const newButton = mobileMenuButton.cloneNode(true);
    mobileMenuButton.parentNode.replaceChild(newButton, mobileMenuButton);

    // Add click event to button
    newButton.addEventListener('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        console.log('Mobile menu button clicked');
        toggleMobileMenu();
    });

    // Add touch event for better mobile support
    newButton.addEventListener('touchstart', function(e) {
        e.preventDefault();
        e.stopPropagation();
        console.log('Mobile menu button touched');
        toggleMobileMenu();
    });

    // Close menu when clicking on links
    const mobileMenuLinks = mobileMenu.querySelectorAll('a');
    mobileMenuLinks.forEach(function(link) {
        link.addEventListener('click', function() {
            console.log('Mobile menu link clicked, closing menu');
            closeMobileMenu();
        });
    });

    // Close menu when clicking outside
    document.addEventListener('click', function(event) {
        if (!mobileMenu.contains(event.target) && 
            !newButton.contains(event.target) && 
            !mobileMenu.classList.contains('hidden')) {
            console.log('Clicked outside mobile menu, closing');
            closeMobileMenu();
        }
    });

    // Close menu on escape key
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Escape' && !mobileMenu.classList.contains('hidden')) {
            console.log('Escape key pressed, closing mobile menu');
            closeMobileMenu();
        }
    });

    console.log('Mobile menu initialized successfully');
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, initializing mobile menu...');
    initMobileMenu();
});

// Also try to initialize immediately in case DOM is already loaded
if (document.readyState === 'loading') {
    // DOM is still loading, wait for DOMContentLoaded
    console.log('DOM is loading, waiting for DOMContentLoaded...');
} else {
    // DOM is already loaded
    console.log('DOM already loaded, initializing immediately...');
    initMobileMenu();
} 