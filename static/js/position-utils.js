/**
 * Centralized position title utilities
 * Used across ballot.html and feed_simple_grid.html
 */

const PositionUtils = {
    /**
     * Get office title for a position level
     */
    getOfficeTitle: function(position_level, translations) {
        const officeTitles = {
            // Database position levels (current)
            'ward_chairperson': translations.ward || 'Ward',
            'ward_member': translations.ward || 'Ward',
            'mayor_chairperson': translations.municipalityRural || 'Municipality/Rural Municipality',
            'deputy_mayor_vice_chairperson': translations.municipalityRural || 'Municipality/Rural Municipality',
            'provincial_assembly': translations.provincialAssembly || 'Provincial Assembly',
            'house_of_representatives': translations.federalParliament || 'Federal Parliament',
            'national_assembly': translations.federalParliament || 'Federal Parliament',

            // Legacy position levels (for backward compatibility)
            'federal': translations.federalParliament || 'Federal Parliament',
            'provincial': translations.provincialAssembly || 'Provincial Assembly',
            'local': translations.localGovernment || 'Local Government',
            'local_executive': translations.municipalityRural || 'Municipality/Rural Municipality',
            'ward': translations.ward || 'Ward'
        };
        return officeTitles[position_level] || position_level;
    },

    /**
     * Get seat description for a position level
     */
    getSeatDescription: function(position_level, translations) {
        const seatTitles = {
            // Database position levels (current)
            'ward_chairperson': translations.wardChairperson || 'Ward Chairperson',
            'ward_member': translations.wardMember || 'Ward Member',
            'mayor_chairperson': translations.mayorChairperson || 'Mayor/Chairperson',
            'deputy_mayor_vice_chairperson': translations.deputyMayorViceChairperson || 'Deputy Mayor/Vice Chairperson',
            'provincial_assembly': translations.provincialAssemblyMember || 'Provincial Assembly Member',
            'house_of_representatives': translations.houseRepresentativesMember || 'House of Representatives Member',
            'national_assembly': translations.nationalAssemblyMember || 'National Assembly Member',

            // Legacy position levels (for backward compatibility)
            'federal': translations.memberParliament || 'Member of Parliament',
            'provincial': translations.provincialAssemblyMember || 'Provincial Assembly Member',
            'local': translations.localRepresentative || 'Local Representative',
            'local_executive': translations.mayorChairperson || 'Mayor/Chairperson',
            'ward': translations.wardRepresentative || 'Ward Representative'
        };
        return seatTitles[position_level] || position_level;
    },

    /**
     * Get position display name (proper title)
     */
    getPositionDisplay: function(position_level, translations) {
        // Map position level to proper display name
        const displayNames = {
            'ward_chairperson': translations.wardChairperson || 'Ward Chairperson',
            'ward_member': translations.wardMember || 'Ward Member',
            'mayor_chairperson': translations.mayorChairperson || 'Mayor/Chairperson',
            'deputy_mayor_vice_chairperson': translations.deputyMayorViceChairperson || 'Deputy Mayor/Vice Chairperson',
            'provincial_assembly': translations.provincialAssemblyMember || 'Provincial Assembly Member',
            'house_of_representatives': translations.houseRepresentativesMember || 'House of Representatives Member',
            'national_assembly': translations.nationalAssemblyMember || 'National Assembly Member',
            'federal': translations.federalCandidate || 'Federal Candidate',
            'provincial': translations.provincialCandidate || 'Provincial Candidate',
            'local': translations.localCandidate || 'Local Candidate',
            'local_executive': translations.localExecutive || 'Local Executive',
            'ward': translations.wardCandidate || 'Ward Candidate'
        };
        return displayNames[position_level] || position_level;
    }
};

// Export for use in templates
if (typeof module !== 'undefined' && module.exports) {
    module.exports = PositionUtils;
}