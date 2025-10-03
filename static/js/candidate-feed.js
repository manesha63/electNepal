/**
 * ElectNepal Candidate Feed Scripts
 * Handles all feed-related functionality without inline scripts for CSP compliance
 */

// Alpine.js Component for Candidate Grid
function candidateGrid() {
    return {
        candidates: [],
        visibleCandidates: [],
        currentPage: 1,
        totalPages: 1,
        pageSize: 9, // 3 rows * 3 columns
        hasMore: true,
        hasPrevious: false,
        searchQuery: '',
        currentLanguage: 'en',

        async fetchCandidates(page = 1) {
            try {
                // Get all parameters from URL
                const urlParams = new URLSearchParams(window.location.search);
                this.searchQuery = urlParams.get('q') || document.getElementById('searchInput')?.value || '';

                // Build query params including filters
                const params = new URLSearchParams();
                params.set('page', page);
                params.set('page_size', 9); // Fixed 3x3 grid

                // Add search query if exists
                if (this.searchQuery) params.set('q', this.searchQuery);

                // Add filter parameters from URL
                if (urlParams.get('province')) params.set('province', urlParams.get('province'));
                if (urlParams.get('district')) params.set('district', urlParams.get('district'));
                if (urlParams.get('municipality')) params.set('municipality', urlParams.get('municipality'));
                if (urlParams.get('position')) params.set('position', urlParams.get('position'));

                // Get the current language prefix from URL
                const currentPath = window.location.pathname;
                const langPrefix = currentPath.startsWith('/ne/') ? '/ne' : '';

                const response = await fetch(`${langPrefix}/candidates/api/cards/?${params.toString()}`);
                const data = await response.json();

                this.candidates = data.items || [];
                this.visibleCandidates = this.candidates;
                this.currentPage = data.page || 1;
                this.totalPages = data.num_pages || 1;
                this.hasMore = data.has_next || false;
                this.hasPrevious = data.has_previous || false;

            } catch (error) {
                console.error('Error fetching candidates:', error);
                // Fallback to template data if available
                this.loadFallbackData();
            }
        },

        loadMore() {
            if (this.hasMore) {
                this.fetchCandidates(this.currentPage + 1);
            }
        },

        loadPrevious() {
            if (this.hasPrevious) {
                this.fetchCandidates(this.currentPage - 1);
            }
        },

        getColumnCount() {
            const width = window.innerWidth;
            if (width >= 1280) return 4; // xl
            if (width >= 1024) return 3; // lg
            if (width >= 640) return 2;  // sm
            return 1;
        },

        formatLocation(candidate) {
            const parts = [];
            // Ward should be an integer, display as "Ward X" or "वडा X"
            if (candidate.ward && typeof candidate.ward === 'number') {
                const wardLabel = this.currentLanguage === 'ne' ? 'वडा' : 'Ward';
                parts.push(`${wardLabel} ${candidate.ward}`);
            }
            // Municipality, District, Province should be strings
            if (candidate.municipality && typeof candidate.municipality === 'string') {
                parts.push(candidate.municipality);
            }
            if (candidate.district && typeof candidate.district === 'string') {
                parts.push(candidate.district);
            }
            if (candidate.province && typeof candidate.province === 'string') {
                parts.push(candidate.province);
            }
            return parts.join(', ') || 'Nepal';
        },

        getOfficeDisplay(office) {
            // Display the office field value
            const officeMap = {
                'federal': this.currentLanguage === 'ne' ? 'संघीय' : 'Federal',
                'provincial': this.currentLanguage === 'ne' ? 'प्रादेशिक' : 'Provincial',
                'municipal': this.currentLanguage === 'ne' ? 'नगरपालिका' : 'Municipal',
                'ward': this.currentLanguage === 'ne' ? 'वडा' : 'Ward'
            };
            return officeMap[office] || office;
        },

        getSeatDescription(position_level) {
            const translations = {
                wardChairperson: this.currentLanguage === 'ne' ? 'वडा अध्यक्ष' : 'Ward Chairperson',
                wardMember: this.currentLanguage === 'ne' ? 'वडा सदस्य' : 'Ward Member',
                mayorChairperson: this.currentLanguage === 'ne' ? 'मेयर/अध्यक्ष' : 'Mayor/Chairperson',
                deputyMayorViceChairperson: this.currentLanguage === 'ne' ? 'उपमेयर/उपाध्यक्ष' : 'Deputy Mayor/Vice Chairperson',
                provincialAssemblyMember: this.currentLanguage === 'ne' ? 'प्रादेशिक सभा सदस्य' : 'Provincial Assembly Member',
                houseRepresentativesMember: this.currentLanguage === 'ne' ? 'प्रतिनिधि सभा सदस्य' : 'House of Representatives Member',
                nationalAssemblyMember: this.currentLanguage === 'ne' ? 'राष्ट्रिय सभा सदस्य' : 'National Assembly Member',
                memberParliament: this.currentLanguage === 'ne' ? 'संसद सदस्य' : 'Member of Parliament',
                localRepresentative: this.currentLanguage === 'ne' ? 'स्थानीय प्रतिनिधि' : 'Local Representative',
                wardRepresentative: this.currentLanguage === 'ne' ? 'वडा प्रतिनिधि' : 'Ward Representative'
            };
            return PositionUtils ? PositionUtils.getSeatDescription(position_level, translations) : (translations[position_level] || position_level);
        },

        shareCandidate(id) {
            // Implement share functionality
            if (navigator.share) {
                navigator.share({
                    title: this.currentLanguage === 'ne' ? 'यो उम्मेदवार हेर्नुहोस्' : 'Check out this candidate',
                    url: `/candidates/${id}/`
                });
            } else {
                // Fallback to copying URL
                const url = `${window.location.origin}/candidates/${id}/`;
                navigator.clipboard.writeText(url);
                alert(this.currentLanguage === 'ne' ? 'लिंक प्रतिलिपि गरियो!' : 'Link copied to clipboard!');
            }
        },

        loadFallbackData() {
            // Use data from window.ELECTNEPAL_FALLBACK_CANDIDATES (injected by template)
            if (window.ELECTNEPAL_FALLBACK_CANDIDATES) {
                this.candidates = window.ELECTNEPAL_FALLBACK_CANDIDATES;
            }
            this.visibleCandidates = this.candidates.slice(0, this.pageSize);
            this.hasMore = this.candidates.length > this.pageSize;
        }
    }
}

// Filter Component for hierarchical location search
function filterComponent() {
    return {
        provinces: [],
        districts: [],
        municipalities: [],
        selectedProvince: '',
        selectedDistrict: '',
        selectedMunicipality: '',
        selectedPosition: '',
        currentLanguage: 'en',

        async init() {
            // Load provinces on initialization
            await this.loadProvinces();
        },

        async loadProvinces() {
            try {
                // Load provinces from window.ELECTNEPAL_PROVINCES (injected by template)
                if (window.ELECTNEPAL_PROVINCES) {
                    this.provinces = window.ELECTNEPAL_PROVINCES;
                }
            } catch (error) {
                console.error('Error loading provinces:', error);
            }
        },

        async loadDistricts() {
            if (!this.selectedProvince) {
                this.districts = [];
                this.municipalities = [];
                this.selectedDistrict = '';
                this.selectedMunicipality = '';
                return;
            }

            try {
                const response = await fetch(`/api/districts/?province=${this.selectedProvince}`);
                this.districts = await response.json();
                this.municipalities = [];
                this.selectedDistrict = '';
                this.selectedMunicipality = '';
            } catch (error) {
                console.error('Error loading districts:', error);
            }
        },

        async loadMunicipalities() {
            if (!this.selectedDistrict) {
                this.municipalities = [];
                this.selectedMunicipality = '';
                return;
            }

            try {
                const response = await fetch(`/api/municipalities/?district=${this.selectedDistrict}`);
                this.municipalities = await response.json();
                this.selectedMunicipality = '';
            } catch (error) {
                console.error('Error loading municipalities:', error);
            }
        },

        applyFilters() {
            const params = new URLSearchParams();
            if (this.selectedProvince) params.set('province', this.selectedProvince);
            if (this.selectedDistrict) params.set('district', this.selectedDistrict);
            if (this.selectedMunicipality) params.set('municipality', this.selectedMunicipality);
            if (this.selectedPosition) params.set('position', this.selectedPosition);

            const searchQuery = document.getElementById('searchInput')?.value;
            if (searchQuery) params.set('q', searchQuery);

            // Preserve language in URL
            const currentPath = window.location.pathname;
            const langPrefix = currentPath.startsWith('/ne/') ? '/ne' : '';

            window.location.href = `${langPrefix}/?${params.toString()}`;
        },

        clearFilters() {
            this.selectedProvince = '';
            this.selectedDistrict = '';
            this.selectedMunicipality = '';
            this.selectedPosition = '';
            this.districts = [];
            this.municipalities = [];

            // Clear and reload without filters
            const currentPath = window.location.pathname;
            const langPrefix = currentPath.startsWith('/ne/') ? '/ne' : '';
            window.location.href = `${langPrefix}/`;
        }
    }
}

// Debounce timer for search
let searchTimeout = null;

// Handle search input with debouncing
function handleSearchInput() {
    // Clear any existing timeout
    if (searchTimeout) {
        clearTimeout(searchTimeout);
    }

    // Set a new timeout for 300ms
    searchTimeout = setTimeout(() => {
        performSearch();
    }, 300);
}

// Keep existing search and filter functions
function performSearch() {
    const searchTerm = document.getElementById('searchInput').value;

    // If using Alpine.js data binding, update the search and fetch
    if (window.Alpine && document.querySelector('[x-data="candidateGrid()"]')) {
        const alpineData = Alpine.$data(document.querySelector('[x-data="candidateGrid()"]'));
        if (alpineData) {
            alpineData.searchQuery = searchTerm;
            alpineData.currentPage = 1;
            alpineData.candidates = [];
            alpineData.fetchCandidates();
            return;
        }
    }

    // Fallback to page reload if Alpine not available
    window.location.href = `?q=${encodeURIComponent(searchTerm)}`;
}

function toggleFilterDropdown() {
    const dropdown = document.getElementById('filterDropdown');
    const button = document.getElementById('filterToggleBtn');
    const isOpen = dropdown.classList.contains('show');

    dropdown.classList.toggle('show');
    button.setAttribute('aria-expanded', !isOpen);

    // Focus management for keyboard users
    if (!isOpen) {
        // When opening, focus first focusable element in dropdown
        setTimeout(() => {
            const firstFocusable = dropdown.querySelector('select, button, input, [tabindex]:not([tabindex="-1"])');
            if (firstFocusable) firstFocusable.focus();
        }, 100);
    }
}

// Close dropdown with Escape key
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        const dropdown = document.getElementById('filterDropdown');
        const button = document.getElementById('filterToggleBtn');
        if (dropdown && dropdown.classList.contains('show')) {
            dropdown.classList.remove('show');
            button.setAttribute('aria-expanded', 'false');
            button.focus();
        }
    }
});

// Export functions for use in templates
if (typeof window !== 'undefined') {
    window.candidateGrid = candidateGrid;
    window.filterComponent = filterComponent;
    window.handleSearchInput = handleSearchInput;
    window.performSearch = performSearch;
    window.toggleFilterDropdown = toggleFilterDropdown;
}
