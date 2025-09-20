// Shared candidate card functions
const candidateCardUtils = {
    formatLocation(candidate) {
        const parts = [];
        // Ward should be an integer, display as "Ward X"
        if (candidate.ward && typeof candidate.ward === 'number') {
            parts.push(`Ward ${candidate.ward}`);
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

    getOfficeTitle(position_level, translations) {
        const officeTitles = {
            'federal': translations.federal_parliament || 'Federal Parliament',
            'provincial': translations.provincial_assembly || 'Provincial Assembly',
            'mayor': translations.municipality || 'Municipality',
            'deputy_mayor': translations.municipality || 'Municipality',
            'ward': translations.ward || 'Ward',
            'local': translations.local_government || 'Local Government',
            'local_executive': translations.municipality_rural || 'Municipality/Rural Municipality'
        };
        return officeTitles[position_level] || translations.independent || 'Independent';
    },

    getSeatDescription(position_level, translations) {
        const seatTitles = {
            'federal': translations.member_parliament || 'Member of Parliament',
            'provincial': translations.provincial_member || 'Provincial Assembly Member',
            'mayor': translations.mayor || 'Mayor',
            'deputy_mayor': translations.deputy_mayor || 'Deputy Mayor',
            'ward': translations.ward_chairperson || 'Ward Chairperson',
            'local': translations.local_representative || 'Local Representative',
            'local_executive': translations.mayor_chairperson || 'Mayor/Chairperson'
        };
        return seatTitles[position_level] || position_level;
    },

    navigateToProfile(candidateId) {
        window.location.href = `/candidates/${candidateId}/`;
    }
};