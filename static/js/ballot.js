/**
 * ElectNepal Ballot Scripts
 * Handles all ballot-related functionality without inline scripts for CSP compliance
 */

function ballotApp() {
    return {
        loading: false,
        error: null,
        searched: false,
        candidates: [],
        currentLanguage: 'en',  // Will be set in x-init

        // Pagination data
        currentPage: 1,
        totalPages: 1,
        totalCandidates: 0,
        pageSize: 20,
        hasNext: false,
        hasPrevious: false,

        // Location selection
        selectedProvince: '',
        selectedDistrict: '',
        selectedMunicipality: '',
        selectedWard: '',

        // Dropdown data
        districts: [],
        municipalities: [],
        maxWards: 50,

        // Request user's location
        async requestLocation() {
            this.loading = true;
            this.error = null;

            if (!navigator.geolocation) {
                this.error = this.translate('Geolocation is not supported by your browser.');
                this.loading = false;
                return;
            }

            navigator.geolocation.getCurrentPosition(
                async (position) => {
                    await this.resolveLocation(position.coords.latitude, position.coords.longitude);
                },
                (error) => {
                    this.loading = false;
                    switch(error.code) {
                        case error.PERMISSION_DENIED:
                            this.error = this.translate('Location permission denied. Please select your location manually.');
                            break;
                        case error.POSITION_UNAVAILABLE:
                            this.error = this.translate('Location information unavailable. Please select manually.');
                            break;
                        case error.TIMEOUT:
                            this.error = this.translate('Location request timed out. Please try again.');
                            break;
                        default:
                            this.error = this.translate('Unable to get your location. Please select manually.');
                    }
                },
                {
                    enableHighAccuracy: false,
                    timeout: 10000,
                    maximumAge: 300000
                }
            );
        },

        // Resolve coordinates to location
        async resolveLocation(lat, lng) {
            try {
                const response = await fetch(`/api/georesolve/?lat=${lat}&lng=${lng}`);
                const data = await response.json();

                if (!response.ok) {
                    throw new Error(data.error || this.translate('Could not determine location'));
                }

                // Set location from resolved data
                if (data.province) {
                    this.selectedProvince = data.province.id;
                    await this.loadDistricts();
                }

                if (data.district) {
                    this.selectedDistrict = data.district.id;
                    await this.loadMunicipalities();
                }

                if (data.municipality) {
                    this.selectedMunicipality = data.municipality.id;
                    await this.updateWardLimit();
                }

                if (data.ward_number) {
                    this.selectedWard = data.ward_number;
                }

                // Load candidates
                await this.loadCandidates();

            } catch (error) {
                this.error = error.message;
            } finally {
                this.loading = false;
            }
        },

        // Load districts for selected province
        async loadDistricts() {
            if (!this.selectedProvince) {
                this.districts = [];
                return;
            }

            try {
                const response = await fetch(`/api/districts/?province=${this.selectedProvince}`);
                this.districts = await response.json();
            } catch (error) {
                console.error('Error loading districts:', error);
            }
        },

        // Load municipalities for selected district
        async loadMunicipalities() {
            if (!this.selectedDistrict) {
                this.municipalities = [];
                return;
            }

            try {
                const response = await fetch(`/api/municipalities/?district=${this.selectedDistrict}`);
                this.municipalities = await response.json();
            } catch (error) {
                console.error('Error loading municipalities:', error);
            }
        },

        // Update ward limit based on selected municipality
        async updateWardLimit() {
            if (!this.selectedMunicipality) {
                this.maxWards = 50;
                return;
            }

            const muni = this.municipalities.find(m => m.id == this.selectedMunicipality);
            if (muni) {
                this.maxWards = muni.total_wards || 50;
            }
        },

        // Search manually with selected location
        async searchManual() {
            if (!this.selectedProvince) {
                this.error = this.translate('Please select a province');
                return;
            }
            if (!this.selectedWard) {
                this.error = this.translate('Please enter a ward number');
                return;
            }

            await this.loadCandidates();
        },

        // Load candidates based on location with frontend caching and pagination
        async loadCandidates(page = 1) {
            this.loading = true;
            this.error = null;

            // Create cache key for localStorage including page
            const cacheKey = `ballot_${this.selectedProvince || ''}_${this.selectedDistrict || ''}_${this.selectedMunicipality || ''}_${this.selectedWard || ''}_${document.documentElement.lang || 'en'}_page${page}`;

            // Try to get cached data (valid for 5 minutes)
            const cachedData = localStorage.getItem(cacheKey);
            if (cachedData) {
                try {
                    const cached = JSON.parse(cachedData);
                    const cacheAge = Date.now() - cached.timestamp;

                    // If cache is less than 5 minutes old (300000 ms), use it
                    if (cacheAge < 300000) {
                        const data = cached.data;
                        this.candidates = data.candidates || [];
                        this.currentPage = data.page || 1;
                        this.totalPages = data.num_pages || 1;
                        this.totalCandidates = data.total || 0;
                        this.hasNext = data.has_next || false;
                        this.hasPrevious = data.has_previous || false;
                        this.searched = true;
                        this.loading = false;
                        console.log('Using cached ballot data for page', page);
                        return;
                    }
                } catch (e) {
                    // Invalid cache data, remove it
                    localStorage.removeItem(cacheKey);
                }
            }

            const params = new URLSearchParams({
                province_id: this.selectedProvince || '',
                district_id: this.selectedDistrict || '',
                municipality_id: this.selectedMunicipality || '',
                ward_number: this.selectedWard || '',
                page: page,
                page_size: this.pageSize
            });

            try {
                const response = await fetch(`/candidates/api/my-ballot/?${params}`);
                const data = await response.json();

                if (!response.ok) {
                    throw new Error(data.error || this.translate('Failed to load candidates'));
                }

                this.candidates = data.candidates || [];
                this.currentPage = data.page || 1;
                this.totalPages = data.num_pages || 1;
                this.totalCandidates = data.total || 0;
                this.hasNext = data.has_next || false;
                this.hasPrevious = data.has_previous || false;
                this.searched = true;

                // Cache the successful result
                try {
                    localStorage.setItem(cacheKey, JSON.stringify({
                        timestamp: Date.now(),
                        data: data
                    }));

                    // Clean up old cache entries (keep only last 10)
                    this.cleanupOldCache();
                } catch (e) {
                    // localStorage might be full or disabled
                    console.warn('Could not cache ballot data:', e);
                }

            } catch (error) {
                this.error = error.message;
            } finally {
                this.loading = false;
            }
        },

        // Navigate to next page
        async nextPage() {
            if (this.hasNext) {
                await this.loadCandidates(this.currentPage + 1);
                window.scrollTo({ top: 0, behavior: 'smooth' });
            }
        },

        // Navigate to previous page
        async previousPage() {
            if (this.hasPrevious) {
                await this.loadCandidates(this.currentPage - 1);
                window.scrollTo({ top: 0, behavior: 'smooth' });
            }
        },

        // Navigate to specific page
        async goToPage(pageNumber) {
            if (pageNumber >= 1 && pageNumber <= this.totalPages) {
                await this.loadCandidates(pageNumber);
                window.scrollTo({ top: 0, behavior: 'smooth' });
            }
        },

        // Clean up old ballot cache entries
        cleanupOldCache() {
            const ballotKeys = [];
            for (let i = 0; i < localStorage.length; i++) {
                const key = localStorage.key(i);
                if (key && key.startsWith('ballot_')) {
                    ballotKeys.push(key);
                }
            }

            // If more than 10 ballot caches, remove oldest ones
            if (ballotKeys.length > 10) {
                const keysWithTime = ballotKeys.map(key => {
                    try {
                        const data = JSON.parse(localStorage.getItem(key));
                        return { key, timestamp: data.timestamp || 0 };
                    } catch {
                        return { key, timestamp: 0 };
                    }
                });

                keysWithTime.sort((a, b) => a.timestamp - b.timestamp);
                const toRemove = keysWithTime.slice(0, keysWithTime.length - 10);
                toRemove.forEach(item => localStorage.removeItem(item.key));
            }
        },

        // Helper functions for displaying candidate cards
        formatLocation(candidate) {
            const parts = [];
            // Ward should be an integer, display as "Ward X"
            if (candidate.ward && typeof candidate.ward === 'number') {
                const wardLabel = this.translate('Ward');
                parts.push(`${wardLabel} ${candidate.ward}`);
            }
            // Municipality, District, Province should be strings
            if (candidate.municipality && typeof candidate.municipality === 'string') {
                parts.push(candidate.municipality);
            }
            if (candidate.district && typeof candidate.district === 'string') {
                parts.push(candidate.district);
            }
            // Don't show province for federal candidates as it's redundant
            if (candidate.province && typeof candidate.province === 'string' && candidate.position_level !== 'federal') {
                parts.push(candidate.province);
            }
            return parts.join(', ') || 'Nepal';
        },

        getOfficeTitle(position_level) {
            const translations = {
                ward: this.translate('Ward'),
                municipalityRural: this.translate('Municipality/Rural Municipality'),
                provincialAssembly: this.translate('Provincial Assembly'),
                federalParliament: this.translate('Federal Parliament'),
                localGovernment: this.translate('Local Government')
            };
            return PositionUtils ? PositionUtils.getOfficeTitle(position_level, translations) : (translations[position_level] || position_level);
        },

        getSeatDescription(position_level) {
            const translations = {
                wardChairperson: this.translate('Ward Chairperson'),
                wardMember: this.translate('Ward Member'),
                mayorChairperson: this.translate('Mayor/Chairperson'),
                deputyMayorViceChairperson: this.translate('Deputy Mayor/Vice Chairperson'),
                provincialAssemblyMember: this.translate('Provincial Assembly Member'),
                houseRepresentativesMember: this.translate('House of Representatives Member'),
                nationalAssemblyMember: this.translate('National Assembly Member'),
                memberParliament: this.translate('Member of Parliament'),
                localRepresentative: this.translate('Local Representative'),
                wardRepresentative: this.translate('Ward Representative')
            };
            return PositionUtils ? PositionUtils.getSeatDescription(position_level, translations) : (translations[position_level] || position_level);
        },

        shareCandidate(candidateId) {
            const shareUrl = `${window.location.origin}/candidates/${candidateId}/`;
            const shareText = this.translate('Check out this independent candidate');

            if (navigator.share) {
                navigator.share({
                    title: shareText,
                    url: shareUrl
                }).catch(err => console.log('Error sharing:', err));
            } else {
                // Fallback to copying URL
                navigator.clipboard.writeText(shareUrl).then(() => {
                    alert(this.translate('Link copied to clipboard!'));
                }).catch(err => {
                    alert(this.translate('Could not copy link'));
                });
            }
        },

        // Simple translation helper
        translate(text) {
            // Basic translation map - can be extended
            const translations = {
                en: {
                    'Ward': 'Ward',
                    'Municipality/Rural Municipality': 'Municipality/Rural Municipality',
                    'Provincial Assembly': 'Provincial Assembly',
                    'Federal Parliament': 'Federal Parliament',
                    'Local Government': 'Local Government',
                    'Ward Chairperson': 'Ward Chairperson',
                    'Ward Member': 'Ward Member',
                    'Mayor/Chairperson': 'Mayor/Chairperson',
                    'Deputy Mayor/Vice Chairperson': 'Deputy Mayor/Vice Chairperson',
                    'Provincial Assembly Member': 'Provincial Assembly Member',
                    'House of Representatives Member': 'House of Representatives Member',
                    'National Assembly Member': 'National Assembly Member',
                    'Member of Parliament': 'Member of Parliament',
                    'Local Representative': 'Local Representative',
                    'Ward Representative': 'Ward Representative',
                    'Check out this independent candidate': 'Check out this independent candidate',
                    'Link copied to clipboard!': 'Link copied to clipboard!',
                    'Could not copy link': 'Could not copy link',
                    'Geolocation is not supported by your browser.': 'Geolocation is not supported by your browser.',
                    'Location permission denied. Please select your location manually.': 'Location permission denied. Please select your location manually.',
                    'Location information unavailable. Please select manually.': 'Location information unavailable. Please select manually.',
                    'Location request timed out. Please try again.': 'Location request timed out. Please try again.',
                    'Unable to get your location. Please select manually.': 'Unable to get your location. Please select manually.',
                    'Could not determine location': 'Could not determine location',
                    'Please select a province': 'Please select a province',
                    'Please enter a ward number': 'Please enter a ward number',
                    'Failed to load candidates': 'Failed to load candidates'
                },
                ne: {
                    'Ward': 'वडा',
                    'Municipality/Rural Municipality': 'नगरपालिका/गाउँपालिका',
                    'Provincial Assembly': 'प्रादेशिक सभा',
                    'Federal Parliament': 'संघीय संसद',
                    'Local Government': 'स्थानीय सरकार',
                    'Ward Chairperson': 'वडा अध्यक्ष',
                    'Ward Member': 'वडा सदस्य',
                    'Mayor/Chairperson': 'मेयर/अध्यक्ष',
                    'Deputy Mayor/Vice Chairperson': 'उपमेयर/उपाध्यक्ष',
                    'Provincial Assembly Member': 'प्रादेशिक सभा सदस्य',
                    'House of Representatives Member': 'प्रतिनिधि सभा सदस्य',
                    'National Assembly Member': 'राष्ट्रिय सभा सदस्य',
                    'Member of Parliament': 'संसद सदस्य',
                    'Local Representative': 'स्थानीय प्रतिनिधि',
                    'Ward Representative': 'वडा प्रतिनिधि',
                    'Check out this independent candidate': 'यो स्वतन्त्र उम्मेदवार हेर्नुहोस्',
                    'Link copied to clipboard!': 'लिंक क्लिपबोर्डमा प्रतिलिपि गरियो!',
                    'Could not copy link': 'लिंक प्रतिलिपि गर्न सकिएन',
                    'Geolocation is not supported by your browser.': 'तपाईंको ब्राउजरले भौगोलिक स्थान समर्थन गर्दैन।',
                    'Location permission denied. Please select your location manually.': 'स्थान अनुमति अस्वीकार गरियो। कृपया म्यानुअल रूपमा आफ्नो स्थान चयन गर्नुहोस्।',
                    'Location information unavailable. Please select manually.': 'स्थान जानकारी उपलब्ध छैन। कृपया म्यानुअल रूपमा चयन गर्नुहोस्।',
                    'Location request timed out. Please try again.': 'स्थान अनुरोध समय समाप्त भयो। कृपया पुन: प्रयास गर्नुहोस्।',
                    'Unable to get your location. Please select manually.': 'तपाईंको स्थान प्राप्त गर्न असमर्थ। कृपया म्यानुअल रूपमा चयन गर्नुहोस्।',
                    'Could not determine location': 'स्थान निर्धारण गर्न सकिएन',
                    'Please select a province': 'कृपया प्रदेश चयन गर्नुहोस्',
                    'Please enter a ward number': 'कृपया वडा नम्बर प्रविष्ट गर्नुहोस्',
                    'Failed to load candidates': 'उम्मेदवारहरू लोड गर्न असफल'
                }
            };

            return translations[this.currentLanguage]?.[text] || text;
        }
    }
}

// Export functions for use in templates
if (typeof window !== 'undefined') {
    window.ballotApp = ballotApp;
}
