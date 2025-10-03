/**
 * ElectNepal Secure Event Handlers
 * All inline event handlers moved here for CSP compliance
 * This removes the need for 'unsafe-inline' in CSP headers
 */

// Initialize all event handlers when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Cookie consent handlers
    const cookieAcceptBtn = document.querySelector('.cookie-accept');
    if (cookieAcceptBtn) {
        cookieAcceptBtn.addEventListener('click', function() {
            if (typeof ElectNepal !== 'undefined' && ElectNepal.acceptCookies) {
                ElectNepal.acceptCookies();
            }
        });
    }

    const cookieSettingsBtn = document.querySelector('.cookie-settings');
    if (cookieSettingsBtn) {
        cookieSettingsBtn.addEventListener('click', function() {
            if (typeof ElectNepal !== 'undefined' && ElectNepal.showCookieSettings) {
                ElectNepal.showCookieSettings();
            }
        });
    }

    // Mobile menu toggle
    const mobileMenuToggle = document.querySelector('.mobile-menu-toggle');
    if (mobileMenuToggle) {
        mobileMenuToggle.addEventListener('click', function() {
            if (typeof toggleMobileMenu === 'function') {
                toggleMobileMenu();
            }
        });
    }

    // Language switcher buttons
    const langBtns = document.querySelectorAll('.lang-btn, [data-lang-switch]');
    langBtns.forEach(function(btn) {
        btn.addEventListener('click', function() {
            if (typeof switchLanguage === 'function') {
                switchLanguage();
            }
        });

        btn.addEventListener('keydown', function(event) {
            if (event.key === 'Enter' || event.key === ' ') {
                event.preventDefault();
                if (typeof switchLanguage === 'function') {
                    switchLanguage();
                }
            }
        });
    });

    // Mobile language switch
    const mobileLangSwitch = document.querySelector('.mobile-lang-switch button');
    if (mobileLangSwitch) {
        mobileLangSwitch.addEventListener('click', function() {
            if (typeof switchLanguage === 'function') {
                switchLanguage();
            }
        });
    }

    // Coming Soon Modal handlers
    const comingSoonModal = document.getElementById('comingSoonModal');
    if (comingSoonModal) {
        comingSoonModal.addEventListener('keydown', function(event) {
            if (event.key === 'Escape' && typeof hideComingSoon === 'function') {
                hideComingSoon();
            }
        });
    }

    const comingSoonOkBtn = document.getElementById('comingSoonOkBtn');
    if (comingSoonOkBtn) {
        comingSoonOkBtn.addEventListener('click', function() {
            if (typeof hideComingSoon === 'function') {
                hideComingSoon();
            }
        });

        comingSoonOkBtn.addEventListener('keydown', function(event) {
            if (event.key === 'Enter' || event.key === ' ') {
                event.preventDefault();
                if (typeof hideComingSoon === 'function') {
                    hideComingSoon();
                }
            }
        });
    }

    // Search functionality
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            if (typeof handleSearchInput === 'function') {
                handleSearchInput();
            }
        });

        searchInput.addEventListener('keypress', function(event) {
            if (event.key === 'Enter') {
                if (typeof searchTimeout !== 'undefined') {
                    clearTimeout(searchTimeout);
                }
                if (typeof performSearch === 'function') {
                    performSearch();
                }
            }
        });
    }

    const searchBtn = document.querySelector('.search-btn');
    if (searchBtn) {
        searchBtn.addEventListener('click', function() {
            if (typeof searchTimeout !== 'undefined') {
                clearTimeout(searchTimeout);
            }
            if (typeof performSearch === 'function') {
                performSearch();
            }
        });
    }

    // Filter dropdown toggle
    const filterToggleBtn = document.getElementById('filterToggleBtn');
    if (filterToggleBtn) {
        filterToggleBtn.addEventListener('click', function() {
            if (typeof toggleFilterDropdown === 'function') {
                toggleFilterDropdown();
            }
        });

        filterToggleBtn.addEventListener('keydown', function(event) {
            if (event.key === 'Enter' || event.key === ' ') {
                event.preventDefault();
                if (typeof toggleFilterDropdown === 'function') {
                    toggleFilterDropdown();
                }
            }
        });
    }

    // Dashboard modal handlers
    const closeModalBtns = document.querySelectorAll('[data-close-modal]');
    closeModalBtns.forEach(function(btn) {
        const modalId = btn.getAttribute('data-close-modal');
        btn.addEventListener('click', function() {
            if (modalId === 'edit' && typeof closeEditModal === 'function') {
                closeEditModal();
            } else if (modalId === 'addPost' && typeof closeAddPostModal === 'function') {
                closeAddPostModal();
            } else if (modalId === 'addEvent' && typeof closeAddEventModal === 'function') {
                closeAddEventModal();
            }
        });
    });

    // Edit profile button
    const editProfileBtn = document.querySelector('[data-action="edit-profile"]');
    if (editProfileBtn) {
        editProfileBtn.addEventListener('click', function() {
            if (typeof openEditModal === 'function') {
                openEditModal();
            }
        });
    }
});

// Global ElectNepal namespace for cookie functions
window.ElectNepal = window.ElectNepal || {};

// Move cookie functions to namespace if not already there
if (!window.ElectNepal.acceptCookies) {
    window.ElectNepal.acceptCookies = function() {
        localStorage.setItem('electnepal_cookie_consent', 'accepted');
        localStorage.setItem('electnepal_cookie_date', new Date().toISOString());
        const cookieBanner = document.getElementById('cookieConsent');
        if (cookieBanner) {
            cookieBanner.classList.remove('show');
            setTimeout(() => {
                cookieBanner.style.display = 'none';
            }, 300);
        }
        console.log('Cookies accepted');
    };
}

if (!window.ElectNepal.showCookieSettings) {
    window.ElectNepal.showCookieSettings = function() {
        alert(typeof gettext !== 'undefined' ? gettext('Cookie settings feature coming soon!') : 'Cookie settings feature coming soon!');
    };
}