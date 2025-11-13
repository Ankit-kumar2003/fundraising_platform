// Mobile menu functionality - improved and more reliable
function initMobileMenu() {
    const mobileMenuButton = document.getElementById('mobile-menu-button');
    const mobileMenu = document.getElementById('mobile-menu');
    const mobileMenuClose = document.getElementById('mobile-menu-close');
    
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
            closeMobileMenu();
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
        console.log('Mobile menu closed');
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

    // Close button functionality
    if (mobileMenuClose) {
        mobileMenuClose.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            console.log('Mobile menu close button clicked');
            closeMobileMenu();
        });
    }

    // Close menu when clicking on links
    const mobileMenuLinks = mobileMenu.querySelectorAll('a');
    mobileMenuLinks.forEach(function(link) {
        link.addEventListener('click', function() {
            console.log('Mobile menu link clicked, closing menu');
            closeMobileMenu();
        });
    });

    // Close menu when clicking on backdrop
    mobileMenu.addEventListener('click', function(event) {
        if (event.target === mobileMenu) {
            console.log('Clicked on backdrop, closing mobile menu');
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

    // Handle orientation change
    window.addEventListener('orientationchange', function() {
        setTimeout(function() {
            if (!mobileMenu.classList.contains('hidden')) {
                console.log('Orientation changed, adjusting mobile menu');
                // Force a reflow to ensure proper positioning
                mobileMenu.style.display = 'none';
                mobileMenu.offsetHeight; // Trigger reflow
                mobileMenu.style.display = '';
            }
        }, 100);
    });

    console.log('Mobile menu initialized successfully');
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, initializing components...');
    initMobileMenu();
    initPasswordStrengthIndicator();
});

// Also try to initialize immediately in case DOM is already loaded
if (document.readyState === 'loading') {
    // DOM is still loading, wait for DOMContentLoaded
    console.log('DOM is loading, waiting for DOMContentLoaded...');
} else {
    // DOM is already loaded
    console.log('DOM already loaded, initializing immediately...');
    initMobileMenu();
    initPasswordStrengthIndicator();
}

// Password strength indicator functionality
function initPasswordStrengthIndicator() {
    const passwordInput = document.querySelector('input[name="password1"]');
    
    if (!passwordInput) {
        console.log('Password input not found on this page');
        return;
    }

    console.log('Password input found, initializing strength indicator...');
    
    // Get all the necessary elements
    const strengthText = document.getElementById('password-strength-text');
    const strengthBar = document.getElementById('password-strength-bar');
    const togglePassword = document.getElementById('togglePassword');
    const lengthCheck = document.getElementById('length-check');
    const uppercaseCheck = document.getElementById('uppercase-check');
    const lowercaseCheck = document.getElementById('lowercase-check');
    const specialCheck = document.getElementById('special-check');
    
    // Add event listener to password input
    passwordInput.addEventListener('input', function() {
        const password = this.value;
        checkPasswordStrength(password);
    });
    
    // Add click event to toggle password visibility
    if (togglePassword) {
        togglePassword.addEventListener('click', function() {
            const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
            passwordInput.setAttribute('type', type);
            this.textContent = type === 'password' ? '👁️' : '👁️‍🗨️';
        });
    }
    
    // Function to check password strength
    function checkPasswordStrength(password) {
        // Reset all checks
        resetChecks();
        
        if (!password) {
            strengthText.textContent = 'Password strength: Not set';
            strengthText.className = 'text-gray-500';
            strengthBar.style.width = '0%';
            strengthBar.className = 'h-full bg-gray-300 transition-all duration-300';
            return;
        }
        
        let strength = 0;
        
        // Check length requirement
        if (password.length >= 8) {
            strength += 25;
            updateCheck(lengthCheck, true);
        }
        
        // Check uppercase requirement
        if (/[A-Z]/.test(password)) {
            strength += 25;
            updateCheck(uppercaseCheck, true);
        }
        
        // Check lowercase requirement
        if (/[a-z]/.test(password)) {
            strength += 25;
            updateCheck(lowercaseCheck, true);
        }
        
        // Check special character requirement
        if (/[!@#$%^&*(),.?":{}|<>]/.test(password)) {
            strength += 25;
            updateCheck(specialCheck, true);
        }
        
        // Update strength indicator
        strengthBar.style.width = `${strength}%`;
        
        // Update strength text and color
        if (strength <= 25) {
            strengthText.textContent = 'Password strength: Very Weak';
            strengthText.className = 'text-red-500';
            strengthBar.className = 'h-full bg-red-500 transition-all duration-300';
        } else if (strength <= 50) {
            strengthText.textContent = 'Password strength: Weak';
            strengthText.className = 'text-orange-500';
            strengthBar.className = 'h-full bg-orange-500 transition-all duration-300';
        } else if (strength <= 75) {
            strengthText.textContent = 'Password strength: Medium';
            strengthText.className = 'text-yellow-500';
            strengthBar.className = 'h-full bg-yellow-500 transition-all duration-300';
        } else {
            strengthText.textContent = 'Password strength: Strong';
            strengthText.className = 'text-green-500';
            strengthBar.className = 'h-full bg-green-500 transition-all duration-300';
        }
    }
    
    // Helper function to reset all requirement checks
    function resetChecks() {
        if (lengthCheck) lengthCheck.textContent = '✗';
        if (uppercaseCheck) uppercaseCheck.textContent = '✗';
        if (lowercaseCheck) lowercaseCheck.textContent = '✗';
        if (specialCheck) specialCheck.textContent = '✗';
        
        if (lengthCheck) lengthCheck.className = 'text-red-500 mr-2';
        if (uppercaseCheck) uppercaseCheck.className = 'text-red-500 mr-2';
        if (lowercaseCheck) lowercaseCheck.className = 'text-red-500 mr-2';
        if (specialCheck) specialCheck.className = 'text-red-500 mr-2';
    }
    
    // Helper function to update a requirement check
    function updateCheck(element, isMet) {
        if (!element) return;
        
        element.textContent = isMet ? '✓' : '✗';
        element.className = isMet ? 'text-green-500 mr-2' : 'text-red-500 mr-2';
    }
    
    console.log('Password strength indicator initialized successfully');
}