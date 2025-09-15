// ElectNepal Main JavaScript

// Cookie Consent Management - Moved to main DOMContentLoaded

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


// Location-based Candidates functionality
let userLocation = null;
let locationPermissionAsked = false;

// Check if location permission has been asked before
function hasLocationPermissionBeenAsked() {
    return localStorage.getItem('electnepal_location_asked') === 'true';
}

// Mark that location permission has been asked
function markLocationPermissionAsked() {
    localStorage.setItem('electnepal_location_asked', 'true');
}

// Request location permission and load candidates
function requestLocationAndLoadCandidates() {
    if (!navigator.geolocation) {
        console.log('Geolocation not supported');
        loadCandidatesByLocation(null);
        return;
    }
    
    showLoading();
    
    navigator.geolocation.getCurrentPosition(
        (position) => {
            userLocation = {
                lat: position.coords.latitude,
                lng: position.coords.longitude
            };
            console.log('User location:', userLocation);
            hideLoading();
            loadCandidatesByLocation(userLocation);
            closeLocationModal();
        },
        (error) => {
            console.error('Location error:', error);
            hideLoading();
            // Load candidates without location
            loadCandidatesByLocation(null);
            closeLocationModal();
        },
        {
            enableHighAccuracy: true,
            timeout: 10000,
            maximumAge: 0
        }
    );
}

// Load candidates based on location
function loadCandidatesByLocation(location) {
    const candidateGrid = document.getElementById('candidateGrid');
    const locationStatus = document.getElementById('locationStatus');
    
    if (!candidateGrid) return;
    
    showLoading();
    
    // Build URL with location parameters
    let url = '/api/nearby-candidates/';
    if (location) {
        url += `?lat=${location.lat}&lng=${location.lng}`;
    }
    
    fetch(url)
        .then(response => response.json())
        .then(data => {
            hideLoading();
            
            // Update location status
            if (locationStatus && data.location) {
                locationStatus.innerHTML = `
                    <i class="fas fa-map-marker-alt"></i>
                    Showing candidates in: <strong>${data.location.municipality}, ${data.location.district}</strong>
                `;
                locationStatus.style.display = 'block';
            }
            
            // Display candidates
            displayCandidates(data.candidates || []);
        })
        .catch(error => {
            console.error('Error loading candidates:', error);
            hideLoading();
            showToast('Error loading candidates. Please try again.', 'error');
        });
}

// Display candidates in the grid
function displayCandidates(candidates) {
    const candidateGrid = document.getElementById('candidateGrid');
    
    if (!candidateGrid) return;
    
    if (candidates.length === 0) {
        candidateGrid.innerHTML = `
            <div style="grid-column: 1/-1; text-align: center; padding: 40px;">
                <i class="fas fa-user-slash" style="font-size: 48px; color: #ccc; margin-bottom: 20px;"></i>
                <p style="color: #666; font-size: 18px;">No candidates found in your area yet.</p>
                <p style="color: #999; margin-top: 10px;">Try adjusting your filters or search in a different location.</p>
            </div>
        `;
        return;
    }
    
    candidateGrid.innerHTML = candidates.map(candidate => `
        <div class="candidate-card">
            ${candidate.photo_url ? 
                `<img src="${candidate.photo_url}" alt="${candidate.name}" class="candidate-photo">` :
                `<div class="candidate-photo-placeholder">
                    <i class="fas fa-user"></i>
                </div>`
            }
            <div class="candidate-info">
                <h3 class="candidate-name">${candidate.name}</h3>
                <p class="candidate-position">${candidate.position}</p>
                <p class="candidate-location">
                    <i class="fas fa-map-marker-alt"></i> ${candidate.municipality}, ${candidate.district}
                </p>
                ${candidate.verified ? 
                    '<span class="verified-badge"><i class="fas fa-check-circle"></i> Verified</span>' : 
                    ''
                }
                <p class="candidate-bio">${candidate.bio}</p>
                <a href="/candidates/${candidate.id}/" class="view-profile-btn">View Profile</a>
            </div>
        </div>
    `).join('');
}

// Close location modal
function closeLocationModal() {
    const modal = document.getElementById('locationModal');
    if (modal) {
        modal.style.display = 'none';
    }
    markLocationPermissionAsked();
}

// Skip location and load all candidates
function skipLocation() {
    closeLocationModal();
    loadCandidatesByLocation(null);
}

// Initialize candidates page
function initCandidatesPage() {
    // Check if we're on the candidates page
    const candidatePage = document.querySelector('.candidates-container');
    if (!candidatePage) return;
    
    // Check if location permission has been asked before
    if (!hasLocationPermissionBeenAsked()) {
        // Show location modal
        const modal = document.getElementById('locationModal');
        if (modal) {
            modal.style.display = 'flex';
        }
    } else {
        // Load candidates without asking for location
        loadCandidatesByLocation(null);
    }
    
    // Initialize search functionality
    const searchInput = document.getElementById('candidateSearch');
    if (searchInput) {
        let searchTimeout;
        searchInput.addEventListener('input', (e) => {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                searchCandidates(e.target.value);
            }, 500);
        });
    }
    
    // Initialize filters
    const filters = document.querySelectorAll('.filter-checkbox');
    filters.forEach(filter => {
        filter.addEventListener('change', applyFilters);
    });
}

// Search candidates
function searchCandidates(query) {
    const url = `/api/search-candidates/?q=${encodeURIComponent(query)}`;
    
    showLoading();
    
    fetch(url)
        .then(response => response.json())
        .then(data => {
            hideLoading();
            displayCandidates(data.results || []);
        })
        .catch(error => {
            console.error('Search error:', error);
            hideLoading();
        });
}

// Apply filters
function applyFilters() {
    const filters = {
        verified: document.getElementById('filterVerified')?.checked,
        hasManifesto: document.getElementById('filterManifesto')?.checked,
        localLevel: document.getElementById('filterLocal')?.checked
    };
    
    // Build query string
    const params = new URLSearchParams();
    if (filters.verified) params.append('verified', 'true');
    if (filters.hasManifesto) params.append('has_manifesto', 'true');
    if (filters.localLevel) params.append('position', 'local');
    
    const url = `/candidates/?${params.toString()}`;
    
    // Reload page with filters (for server-side filtering)
    window.location.href = url;
}

// Main DOMContentLoaded listener - consolidated

// Show Coming Soon modal
function showComingSoon() {
    const modal = document.getElementById('comingSoonModal');
    if (modal) {
        modal.style.display = 'flex';
    }
}

// Hide Coming Soon modal
function hideComingSoon() {
    const modal = document.getElementById('comingSoonModal');
    if (modal) {
        modal.style.display = 'none';
    }
}

// Switch language directly (toggle between EN and NE)
function switchLanguage() {
    let currentPath = window.location.pathname;

    // Check if we're currently in Nepali mode
    const isNepali = currentPath.startsWith('/ne/');

    // Remove existing language prefix if present
    currentPath = currentPath.replace(/^\/ne\//, '/').replace(/^\/en\//, '/');

    // Switch to the opposite language
    if (isNepali) {
        // Currently in Nepali, switch to English
        window.location.href = currentPath;
    } else {
        // Currently in English, switch to Nepali
        window.location.href = '/ne' + currentPath;
    }
}

// Main DOMContentLoaded Event Listener (Consolidated)
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

    // Initialize candidates page if applicable
    initCandidatesPage();

    // Initialize language settings based on URL
    const currentPath = window.location.pathname;
    const isNepali = currentPath.startsWith('/ne/');

    // Just add/remove the body class, don't change button text
    if (isNepali) {
        document.body.classList.add('ne');
        localStorage.setItem('electnepal_language', 'ne');
    } else {
        document.body.classList.remove('ne');
        localStorage.setItem('electnepal_language', 'en');
    }

    // Close dropdown when clicking outside
    document.addEventListener('click', function(e) {
        const switcher = document.querySelector('.language-switcher');
        const dropdown = document.getElementById('langDropdown');
        if (switcher && !switcher.contains(e.target) && dropdown) {
            dropdown.classList.remove('active');
        }
    });
});

// Export functions for use in templates
window.ElectNepal = {
    acceptCookies,
    showCookieSettings,
    showToast,
    showLoading,
    hideLoading,
    switchLanguage,
    toggleLanguage,
    setLanguage,
    requestLocationAndLoadCandidates,
    skipLocation,
    closeLocationModal
};