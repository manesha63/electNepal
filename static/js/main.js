// ElectNepal Main JavaScript

// Cookie Consent Management
document.addEventListener('DOMContentLoaded', function() {
    // Check if user has already accepted cookies
    const cookieConsent = localStorage.getItem('electnepal_cookie_consent');
    
    if (!cookieConsent) {
        // Show cookie consent after a short delay
        setTimeout(() => {
            showCookieConsent();
        }, 1000);
    }
    
    // Initialize animations
    initAnimations();
    
    // Initialize smooth scrolling
    initSmoothScroll();
    
    // Initialize mobile menu if needed
    initMobileMenu();
});

// Show Cookie Consent Banner
function showCookieConsent() {
    const cookieBanner = document.getElementById('cookieConsent');
    if (cookieBanner) {
        cookieBanner.classList.add('show');
    }
}

// Accept Cookies
function acceptCookies() {
    localStorage.setItem('electnepal_cookie_consent', 'accepted');
    localStorage.setItem('electnepal_cookie_date', new Date().toISOString());
    hideCookieConsent();
    
    // Initialize analytics or other cookie-dependent services here
    console.log('Cookies accepted');
}

// Show Cookie Settings (can be expanded later)
function showCookieSettings() {
    alert('Cookie settings feature coming soon! For now, all cookies are essential for the app to function properly.');
}

// Hide Cookie Consent Banner
function hideCookieConsent() {
    const cookieBanner = document.getElementById('cookieConsent');
    if (cookieBanner) {
        cookieBanner.classList.remove('show');
        setTimeout(() => {
            cookieBanner.style.display = 'none';
        }, 300);
    }
}

// Initialize Animations
function initAnimations() {
    // Animate elements on scroll
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);
    
    // Observe all elements with animation classes
    document.querySelectorAll('.animate-on-scroll').forEach(el => {
        observer.observe(el);
    });
}

// Smooth Scroll for anchor links
function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

// Mobile Menu Toggle
function initMobileMenu() {
    const menuToggle = document.getElementById('mobileMenuToggle');
    const mobileMenu = document.getElementById('mobileMenu');
    
    if (menuToggle && mobileMenu) {
        menuToggle.addEventListener('click', () => {
            mobileMenu.classList.toggle('show');
            menuToggle.classList.toggle('active');
        });
        
        // Close menu when clicking outside
        document.addEventListener('click', (e) => {
            if (!menuToggle.contains(e.target) && !mobileMenu.contains(e.target)) {
                mobileMenu.classList.remove('show');
                menuToggle.classList.remove('active');
            }
        });
    }
}

// Language Switcher Enhancement
function switchLanguage(lang) {
    // This will be handled by Django's i18n, but we can add UI feedback
    const switcher = document.querySelector('.language-switcher select');
    if (switcher) {
        switcher.value = lang;
        // Add loading state
        switcher.disabled = true;
        switcher.style.opacity = '0.5';
        
        // Submit the form
        switcher.form.submit();
    }
}

// Add ripple effect to buttons
document.querySelectorAll('.btn').forEach(button => {
    button.addEventListener('click', function(e) {
        const ripple = document.createElement('span');
        const rect = this.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        const x = e.clientX - rect.left - size / 2;
        const y = e.clientY - rect.top - size / 2;
        
        ripple.style.width = ripple.style.height = size + 'px';
        ripple.style.left = x + 'px';
        ripple.style.top = y + 'px';
        ripple.classList.add('ripple');
        
        this.appendChild(ripple);
        
        setTimeout(() => {
            ripple.remove();
        }, 600);
    });
});

// Form validation helper
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

// Show loading state
function showLoading() {
    const loader = document.getElementById('loader');
    if (loader) {
        loader.style.display = 'flex';
    }
}

// Hide loading state
function hideLoading() {
    const loader = document.getElementById('loader');
    if (loader) {
        loader.style.display = 'none';
    }
}

// Toast notification
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    
    document.body.appendChild(toast);
    
    // Trigger animation
    setTimeout(() => {
        toast.classList.add('show');
    }, 10);
    
    // Remove after 3 seconds
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => {
            toast.remove();
        }, 300);
    }, 3000);
}

// Utility function to detect mobile device
function isMobile() {
    return window.innerWidth <= 768;
}

// Add keyboard navigation support
document.addEventListener('keydown', (e) => {
    // Escape key to close modals/menus
    if (e.key === 'Escape') {
        // Close mobile menu if open
        const mobileMenu = document.getElementById('mobileMenu');
        if (mobileMenu && mobileMenu.classList.contains('show')) {
            mobileMenu.classList.remove('show');
        }
        
        // Close cookie consent if open
        const cookieBanner = document.getElementById('cookieConsent');
        if (cookieBanner && cookieBanner.classList.contains('show')) {
            // Don't close automatically - user must make a choice
            console.log('Please accept or configure cookies');
        }
    }
});

// Page visibility API to pause animations when tab is not visible
document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
        // Pause animations
        document.querySelectorAll('.animated').forEach(el => {
            el.style.animationPlayState = 'paused';
        });
    } else {
        // Resume animations
        document.querySelectorAll('.animated').forEach(el => {
            el.style.animationPlayState = 'running';
        });
    }
});

// Export functions for use in templates
window.ElectNepal = {
    acceptCookies,
    showCookieSettings,
    showToast,
    showLoading,
    hideLoading,
    switchLanguage
};