/**
 * ElectNepal Candidate Registration Scripts
 * Handles multi-step registration form without inline scripts for CSP compliance
 */

function registrationForm() {
    return {
        step: 1,
        positionLevel: '',
        submitting: false,
        currentLanguage: 'en',

        init() {
            // Watch position level changes
            const positionSelect = document.getElementById('id_position_level');
            if (positionSelect) {
                positionSelect.addEventListener('change', (e) => {
                    this.positionLevel = e.target.value;
                });
            }

            // Add photo file input validation
            const photoInput = document.getElementById('id_photo');
            if (photoInput) {
                photoInput.addEventListener('change', (e) => {
                    const file = e.target.files[0];
                    if (file) {
                        // Check file type
                        const validTypes = ['image/jpeg', 'image/jpg', 'image/png'];
                        if (!validTypes.includes(file.type)) {
                            const msg = this.currentLanguage === 'ne'
                                ? 'कृपया JPG वा PNG छविहरू मात्र अपलोड गर्नुहोस्'
                                : 'Please upload only JPG or PNG images';
                            alert(msg);
                            e.target.value = '';
                            return;
                        }
                        // Check file size (5MB max)
                        const maxSize = 5 * 1024 * 1024; // 5MB in bytes
                        if (file.size > maxSize) {
                            const msg = this.currentLanguage === 'ne'
                                ? 'छविको आकार 5MB भन्दा कम हुनुपर्छ'
                                : 'Image size must be less than 5MB';
                            alert(msg);
                            e.target.value = '';
                            return;
                        }
                    }
                });
            }

            // Add document file input validation
            const identityDocInput = document.getElementById('id_identity_document');
            const candidacyDocInput = document.getElementById('id_candidacy_document');

            // Validation function for documents
            const validateDocument = (file, inputElement) => {
                if (file) {
                    // Check file type
                    const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'application/pdf'];
                    if (!validTypes.includes(file.type)) {
                        const msg = this.currentLanguage === 'ne'
                            ? 'कृपया JPG, PNG वा PDF कागजातहरू मात्र अपलोड गर्नुहोस्'
                            : 'Please upload only JPG, PNG or PDF documents';
                        alert(msg);
                        inputElement.value = '';
                        return false;
                    }
                    // Check file size (10MB max for documents)
                    const maxSize = 10 * 1024 * 1024; // 10MB in bytes
                    if (file.size > maxSize) {
                        const msg = this.currentLanguage === 'ne'
                            ? 'कागजातको आकार 10MB भन्दा कम हुनुपर्छ'
                            : 'Document size must be less than 10MB';
                        alert(msg);
                        inputElement.value = '';
                        return false;
                    }
                    // Show success message
                    console.log(`Document "${file.name}" selected successfully`);
                }
                return true;
            };

            if (identityDocInput) {
                identityDocInput.addEventListener('change', (e) => {
                    validateDocument(e.target.files[0], e.target);
                });
            }

            if (candidacyDocInput) {
                candidacyDocInput.addEventListener('change', (e) => {
                    validateDocument(e.target.files[0], e.target);
                });
            }

            // Initialize dynamic location dropdowns
            this.initLocationDropdowns();
        },

        nextStep() {
            if (this.validateStep()) {
                this.step++;
                this.updateProgress();
                window.scrollTo(0, 0);
            }
        },

        previousStep() {
            this.step--;
            this.updateProgress();
            window.scrollTo(0, 0);
        },

        updateProgress() {
            const progressBar = document.querySelector('.bg-blue-600');
            if (progressBar) {
                progressBar.style.width = (this.step * 20) + '%';  // 20% for 5 steps
            }

            // Update mobile step indicator
            const mobileStepText = document.querySelector('.sm\\:hidden .font-semibold');
            if (mobileStepText) {
                const stepNames = ['Basic Info', 'Location', 'Content', 'Documents', 'Review'];
                const stepNamesNe = ['आधारभूत जानकारी', 'स्थान', 'सामग्री', 'कागजात', 'समीक्षा'];
                const name = this.currentLanguage === 'ne' ? stepNamesNe[this.step - 1] : stepNames[this.step - 1];
                mobileStepText.textContent = `Step ${this.step} of 5: ${name}`;
            }
        },

        validateStep() {
            // Add validation logic for each step
            if (this.step === 1) {
                // Step 1: Basic Info validation
                const fullName = document.getElementById('id_full_name');
                const age = document.getElementById('id_age');
                const photo = document.getElementById('id_photo');

                if (!fullName || !fullName.value.trim()) {
                    const msg = this.currentLanguage === 'ne'
                        ? 'कृपया आफ्नो पूरा नाम प्रविष्ट गर्नुहोस्'
                        : 'Please enter your full name';
                    alert(msg);
                    return false;
                }
                if (!age || !age.value || age.value < 18) {
                    const msg = this.currentLanguage === 'ne'
                        ? 'कृपया मान्य उमेर प्रविष्ट गर्नुहोस् (१८ वर्ष वा माथि हुनुपर्छ)'
                        : 'Please enter a valid age (must be 18 or older)';
                    alert(msg);
                    return false;
                }
                if (!photo || !photo.files || photo.files.length === 0) {
                    const msg = this.currentLanguage === 'ne'
                        ? 'कृपया आफ्नो प्रोफाइल फोटो अपलोड गर्नुहोस् (आवश्यक)'
                        : 'Please upload your profile photo (required)';
                    alert(msg);
                    return false;
                }
            } else if (this.step === 2) {
                // Step 2: Location validation
                const office = document.getElementById('id_office');
                const position = document.getElementById('id_position_level');
                const province = document.getElementById('id_province');
                const district = document.getElementById('id_district');
                const municipality = document.getElementById('id_municipality');
                const wardNumber = document.getElementById('id_ward_number');

                if (!office || !office.value) {
                    const msg = this.currentLanguage === 'ne' ? 'कृपया कार्यालय चयन गर्नुहोस्' : 'Please select an office';
                    alert(msg);
                    return false;
                }
                if (!position || !position.value) {
                    const msg = this.currentLanguage === 'ne' ? 'कृपया सीट चयन गर्नुहोस्' : 'Please select a seat';
                    alert(msg);
                    return false;
                }
                if (!province || !province.value) {
                    const msg = this.currentLanguage === 'ne' ? 'कृपया प्रदेश चयन गर्नुहोस्' : 'Please select a province';
                    alert(msg);
                    return false;
                }
                if (!district || !district.value) {
                    const msg = this.currentLanguage === 'ne' ? 'कृपया जिल्ला चयन गर्नुहोस्' : 'Please select a district';
                    alert(msg);
                    return false;
                }
                if (!municipality || !municipality.value) {
                    const msg = this.currentLanguage === 'ne'
                        ? 'सबै पदका लागि नगरपालिका आवश्यक छ'
                        : 'Municipality is required for all positions';
                    alert(msg);
                    return false;
                }
                if (!wardNumber || !wardNumber.value) {
                    const msg = this.currentLanguage === 'ne'
                        ? 'सबै पदका लागि वडा नम्बर आवश्यक छ'
                        : 'Ward number is required for all positions';
                    alert(msg);
                    return false;
                }
            } else if (this.step === 3) {
                // Step 3: Content validation
                const bioEn = document.getElementById('id_bio_en');
                const educationEn = document.getElementById('id_education_en');
                const experienceEn = document.getElementById('id_experience_en');
                const achievementsEn = document.getElementById('id_achievements_en');
                const manifestoEn = document.getElementById('id_manifesto_en');

                if (!bioEn || !bioEn.value.trim()) {
                    const msg = this.currentLanguage === 'ne'
                        ? 'कृपया आफ्नो जीवनी प्रविष्ट गर्नुहोस्'
                        : 'Please enter your biography';
                    alert(msg);
                    return false;
                }
                if (!educationEn || !educationEn.value.trim()) {
                    const msg = this.currentLanguage === 'ne'
                        ? 'कृपया आफ्नो शिक्षा विवरण प्रविष्ट गर्नुहोस्'
                        : 'Please enter your education details';
                    alert(msg);
                    return false;
                }
                if (!experienceEn || !experienceEn.value.trim()) {
                    const msg = this.currentLanguage === 'ne'
                        ? 'कृपया आफ्नो अनुभव प्रविष्ट गर्नुहोस्'
                        : 'Please enter your experience';
                    alert(msg);
                    return false;
                }
                if (!achievementsEn || !achievementsEn.value.trim()) {
                    const msg = this.currentLanguage === 'ne'
                        ? 'कृपया आफ्नो मुख्य उपलब्धिहरू प्रविष्ट गर्नुहोस्'
                        : 'Please enter your key achievements';
                    alert(msg);
                    return false;
                }
                if (!manifestoEn || !manifestoEn.value.trim()) {
                    const msg = this.currentLanguage === 'ne'
                        ? 'कृपया आफ्नो घोषणापत्र प्रविष्ट गर्नुहोस्'
                        : 'Please enter your manifesto';
                    alert(msg);
                    return false;
                }
            } else if (this.step === 4) {
                // Step 4: Document validation
                const identityDoc = document.getElementById('id_identity_document');
                const candidacyDoc = document.getElementById('id_candidacy_document');

                if (!identityDoc || !identityDoc.files || identityDoc.files.length === 0) {
                    const msg = this.currentLanguage === 'ne'
                        ? 'कृपया आफ्नो परिचय कागजात अपलोड गर्नुहोस्'
                        : 'Please upload your identity document (National ID/Citizenship/Driver\'s License)';
                    alert(msg);
                    return false;
                }
                if (!candidacyDoc || !candidacyDoc.files || candidacyDoc.files.length === 0) {
                    const msg = this.currentLanguage === 'ne'
                        ? 'कृपया आफ्नो निर्वाचन घोषणा कागजात अपलोड गर्नुहोस्'
                        : 'Please upload your election declaration document';
                    alert(msg);
                    return false;
                }
            }
            return true;
        },

        initLocationDropdowns() {
            const provinceSelect = document.getElementById('id_province');
            const districtSelect = document.getElementById('id_district');
            const municipalitySelect = document.getElementById('id_municipality');
            const wardSelect = document.getElementById('id_ward_number');

            // Store the initially selected values (from server-side validation)
            const initialProvince = provinceSelect ? provinceSelect.value : null;
            const initialDistrict = districtSelect ? districtSelect.value : null;
            const initialMunicipality = municipalitySelect ? municipalitySelect.value : null;
            const initialWard = wardSelect ? wardSelect.value : null;

            if (provinceSelect) {
                provinceSelect.addEventListener('change', async function() {
                    const provinceId = this.value;
                    if (provinceId) {
                        // Fetch districts for this province
                        const response = await fetch(`/api/districts/?province=${provinceId}`);
                        const districts = await response.json();

                        // Update district dropdown
                        districtSelect.innerHTML = '<option value="">Select District</option>';
                        districts.forEach(district => {
                            const option = new Option(district.name_en, district.id);
                            districtSelect.add(option);
                        });

                        // Clear municipality and ward dropdowns
                        municipalitySelect.innerHTML = '<option value="">Select Municipality</option>';
                        if (wardSelect) {
                            wardSelect.innerHTML = '<option value="">Select Ward</option>';
                        }
                    }
                });
            }

            if (districtSelect) {
                districtSelect.addEventListener('change', async function() {
                    const districtId = this.value;
                    if (districtId) {
                        // Fetch municipalities for this district
                        const response = await fetch(`/api/municipalities/?district=${districtId}`);
                        const municipalities = await response.json();

                        // Update municipality dropdown
                        municipalitySelect.innerHTML = '<option value="">Select Municipality</option>';
                        municipalities.forEach(municipality => {
                            const option = new Option(municipality.name_en, municipality.id);
                            municipalitySelect.add(option);
                        });

                        // Clear ward dropdown when district changes
                        if (wardSelect) {
                            wardSelect.innerHTML = '<option value="">Select Ward</option>';
                        }
                    }
                });
            }

            // Add municipality change event listener for ward population
            if (municipalitySelect) {
                municipalitySelect.addEventListener('change', async function() {
                    console.log('Municipality changed:', this.value); // Debug log
                    const municipalityId = this.value;

                    if (municipalityId && wardSelect) {
                        try {
                            // Fetch ward count for this municipality
                            const response = await fetch(`/api/municipalities/${municipalityId}/wards/`);
                            const data = await response.json();
                            console.log('Ward data received:', data); // Debug log

                            // Update ward dropdown
                            // First, clear all options except the first one
                            wardSelect.innerHTML = '<option value="">--- Select Ward ---</option>';

                            // Add ward options
                            for (let i = 1; i <= data.total_wards; i++) {
                                const option = document.createElement('option');
                                option.value = i;
                                option.textContent = `Ward ${i}`;
                                wardSelect.appendChild(option);
                            }
                            console.log(`Added ${data.total_wards} wards to dropdown`); // Debug log
                        } catch (error) {
                            console.error('Error fetching wards:', error);
                            const msg = this.currentLanguage === 'ne'
                                ? 'वडा जानकारी लोड गर्न सकिएन'
                                : 'Error loading ward information. Please try again.';
                            alert(msg);
                        }
                    } else if (wardSelect) {
                        // Clear ward dropdown if no municipality selected
                        wardSelect.innerHTML = '<option value="">--- Select Ward ---</option>';
                    }
                });
            }

            // Restore initial selections if they exist (after validation errors)
            if (initialProvince) {
                // Load districts for the selected province
                this.loadDistrictsForProvince(initialProvince, initialDistrict);

                // If district was also selected, load municipalities
                if (initialDistrict) {
                    this.loadMunicipalitiesForDistrict(initialDistrict, initialMunicipality);

                    // If municipality was also selected, load wards
                    if (initialMunicipality) {
                        this.loadWardsForMunicipality(initialMunicipality, initialWard);
                    }
                }
            }
        },

        async loadDistrictsForProvince(provinceId, selectedDistrictId = null) {
            const districtSelect = document.getElementById('id_district');
            if (provinceId && districtSelect) {
                try {
                    const response = await fetch(`/api/districts/?province=${provinceId}`);
                    const districts = await response.json();

                    // Preserve the current selection if it exists
                    const currentSelection = selectedDistrictId || districtSelect.value;

                    districtSelect.innerHTML = '<option value="">Select District</option>';
                    districts.forEach(district => {
                        const option = new Option(district.name_en, district.id);
                        if (district.id == currentSelection) {
                            option.selected = true;
                        }
                        districtSelect.add(option);
                    });
                } catch (error) {
                    console.error('Error loading districts:', error);
                }
            }
        },

        async loadMunicipalitiesForDistrict(districtId, selectedMunicipalityId = null) {
            const municipalitySelect = document.getElementById('id_municipality');
            if (districtId && municipalitySelect) {
                try {
                    const response = await fetch(`/api/municipalities/?district=${districtId}`);
                    const municipalities = await response.json();

                    // Preserve the current selection if it exists
                    const currentSelection = selectedMunicipalityId || municipalitySelect.value;

                    municipalitySelect.innerHTML = '<option value="">Select Municipality</option>';
                    municipalities.forEach(municipality => {
                        const option = new Option(municipality.name_en, municipality.id);
                        if (municipality.id == currentSelection) {
                            option.selected = true;
                        }
                        municipalitySelect.add(option);
                    });
                } catch (error) {
                    console.error('Error loading municipalities:', error);
                }
            }
        },

        async loadWardsForMunicipality(municipalityId, selectedWardNumber = null) {
            const wardSelect = document.getElementById('id_ward_number');
            if (municipalityId && wardSelect) {
                try {
                    const response = await fetch(`/api/municipalities/${municipalityId}/wards/`);
                    const data = await response.json();

                    // Preserve the current selection if it exists
                    const currentSelection = selectedWardNumber || wardSelect.value;

                    wardSelect.innerHTML = '<option value="">--- Select Ward ---</option>';
                    for (let i = 1; i <= data.total_wards; i++) {
                        const option = document.createElement('option');
                        option.value = i;
                        option.textContent = `Ward ${i}`;
                        if (i == currentSelection) {
                            option.selected = true;
                        }
                        wardSelect.appendChild(option);
                    }
                } catch (error) {
                    console.error('Error loading wards:', error);
                }
            }
        }
    }
}

// Export functions for use in templates
if (typeof window !== 'undefined') {
    window.registrationForm = registrationForm;
}
