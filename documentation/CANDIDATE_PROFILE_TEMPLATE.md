# ElectNepal Candidate Profile Template - STANDARD FORMAT

## IMPORTANT: This is the EXACT template that must be used for ALL candidate profiles

### Template Structure Overview

Every candidate profile MUST contain the following sections in this exact order:

## 1. **Header Section**
- **Photo**: 8.5cm × 9cm (horizontal rectangular format)
  - Position: Top left
  - If no photo: Blue-purple gradient placeholder with first letter of name

## 2. **Below Photo (Centered)**
- **Candidate Name**: Bold, centered below photo
- **Office**: "Office: [Position Level]" (e.g., "Office: Provincial Assembly")
- **Seat**: "Seat: [Specific Position]" (e.g., "Seat: Provincial Assembly Member")

## 3. **Right Side of Photo**
- **From**: Single line format - "[Ward Number], [Municipality], [District], [Province]"
  - Example: "From: Budhanilkantha, Kathmandu, Bagmati"
  - Include Ward only if applicable

### 4. **Education Section**
- **Header**: "Education" (no icon)
- **Format**: Bullet points with degree, institution, and year
- **Example**:
  ```
  • Masters in Public Administration (MPA) - Tribhuvan University (2010)
  • Bachelor of Arts in Political Science - Tribhuvan University (2006)
  • Certificate in Leadership and Governance - Harvard Kennedy School (2018)
  • Diploma in Project Management - Asian Institute of Technology (2015)
  ```

### 5. **Past Experience Section**
- **Header**: "Past Experience" (no icon)
- **Format**: Bullet points with position, organization, and years
- **Key Achievements**: Bold and larger font size
- **Example**:
  ```
  • Executive Director - Community Development Foundation (2015-2023)
  • Program Manager - Nepal Youth Foundation (2010-2015)
  • Social Worker - UNDP Nepal (2008-2010)
  • Youth Coordinator - Red Cross Nepal (2006-2008)

  Key Achievements:
  - Led implementation of clean water projects in 50+ villages
  - Established 15 community health centers
  - Created employment for 500+ youth through skill development programs
  - Initiated digital literacy program reaching 10,000+ students
  ```

### 6. **Full Width Sections (Below Photo and Right Side)**

#### **Motivation Section**
- **Header**: "Motivation" (no icon)
- **Content**: 2-3 paragraphs about:
  - Personal background and experience
  - Vision for the community/country
  - Core beliefs and values
- **Example**:
  ```
  [Name] is a dedicated public servant with over [X] years of experience in [field].
  Born and raised in [location], he/she has witnessed firsthand the challenges
  facing our communities and is committed to bringing positive change.

  His/Her vision is to create a more equitable and prosperous society where
  every citizen has access to quality education, healthcare, and economic
  opportunities. He/She believes in transparent governance, sustainable
  development, and inclusive policies that benefit all sections of society.
  ```

#### **Political Manifesto Section**
- **Header**: "Political Manifesto" (no icon)
- **Format**: Numbered main points with sub-bullets
- **Example Structure**:
  ```
  MY COMMITMENT TO THE PEOPLE:

  1. EDUCATION FOR ALL
  - Free quality education up to grade 12
  - Technical and vocational training centers in every ward
  - Digital classrooms in all public schools
  - Scholarships for underprivileged students

  2. HEALTHCARE ACCESS
  - 24/7 health posts in every ward
  - Free basic healthcare services
  - Mobile health camps for remote areas
  - Mental health support programs

  3. ECONOMIC DEVELOPMENT
  - Support for local entrepreneurs and startups
  - Agricultural modernization programs
  - Tourism development initiatives
  - Youth employment guarantee scheme

  4. INFRASTRUCTURE
  - All-weather roads to every settlement
  - Reliable electricity and internet connectivity
  - Clean drinking water for all households
  - Modern waste management systems

  5. GOOD GOVERNANCE
  - Transparent budget allocation and spending
  - Regular public consultations
  - Zero tolerance for corruption
  - Digital services for all government procedures
  ```

### 7. **Additional Information Cards** (Grid Layout)

#### **Upcoming Events** (with calendar icon)
- **Format**: Event name, date, location
- **Example**:
  ```
  Town Hall Meeting - Budhanilkantha
  Sep 22, 2025
  Community Hall, Ward 3, Budhanilkantha
  ```

#### **Contact** (with address-card icon)
- **Only show fields that are filled**
- **Format**:
  ```
  Email: [email address]
  Phone: [phone number]
  Website: [website URL without http://]
  Social Media: Facebook Profile [linked]
  ```

### 8. **Navigation**
- **Back Button**: "Back to All Candidates" (centered at bottom)

## Template Rules

### MUST HAVE:
1. Photo dimensions: 8.5cm × 9cm
2. Name, Office, Seat below photo (centered)
3. "From:" location in single line format
4. Education and Past Experience on right side of photo
5. Motivation and Political Manifesto full width below
6. "Key Achievements:" in bold and larger font
7. Contact section only shows filled fields

### MUST NOT HAVE:
1. ❌ NO "Verified" badges or verification status
2. ❌ NO "View Profile" buttons (names are clickable instead)
3. ❌ NO "Support Campaign" buttons
4. ❌ NO "Visit Website" button (included in Contact if available)
5. ❌ NO "Facebook" button (included in Contact if available)
6. ❌ NO "Quick Facts" section
7. ❌ NO icons except for Events (calendar) and Contact (address-card)

### Styling Guidelines:
- **Font**: System default with Tailwind CSS
- **Colors**:
  - Primary text: Gray-900
  - Secondary text: Gray-700
  - Location/details: Gray-600
  - Links: Blue-600 with hover effect
- **Spacing**: Consistent padding and margins as defined in template
- **Responsive**: Mobile-friendly with proper breakpoints

## Database Fields Mapping

| Display Field | Database Field | Notes |
|--------------|---------------|-------|
| Name | `candidate.full_name` | |
| Photo | `candidate.photo` | 8.5cm × 9cm |
| Office | `candidate.get_position_level_display()` | |
| Seat | Conditional based on `position_level` | |
| From | `ward_number`, `municipality.name_en`, `district.name_en`, `province.name_en` | |
| Education | `candidate.education_en` or `education_ne` | |
| Past Experience | `candidate.experience_en` or `experience_ne` | |
| Motivation | `candidate.bio_en` or `bio_ne` | |
| Political Manifesto | `candidate.manifesto_en` or `manifesto_ne` | |
| Email | `candidate.user.email` | Only if exists |
| Phone | `candidate.phone_number` | Only if exists |
| Website | `candidate.website` | Only if exists |
| Social Media | `candidate.facebook_url` | Only if exists |

## Implementation Notes

1. **Language Support**: Template automatically switches between English (`_en`) and Nepali (`_ne`) fields based on user language preference
2. **Auto-translation**: Content is automatically translated to Nepali on save if not provided
3. **Key Achievements**: JavaScript automatically makes this text bold and larger
4. **Clickable Names**: Candidate names in feed/list views link directly to profile (no separate button)
5. **Contact Section**: Entire section hidden if no contact information available

## Testing Checklist

Before any candidate profile goes live, verify:
- [ ] Photo displays at correct dimensions (8.5cm × 9cm)
- [ ] Name, Office, Seat are centered below photo
- [ ] Location shows in "From: Ward, Municipality, District, Province" format
- [ ] Education shows with bullet points
- [ ] Past Experience shows with bullet points
- [ ] "Key Achievements:" appears bold and larger
- [ ] Motivation section displays full width
- [ ] Political Manifesto displays with numbered points
- [ ] Contact section only shows filled fields
- [ ] NO verification badges appear
- [ ] NO View Profile, Support, Website, or Facebook buttons
- [ ] Events show with calendar icon
- [ ] Contact shows with address-card icon

---

**Last Updated**: January 19, 2025
**Template Version**: 1.0
**Status**: MANDATORY - All profiles must use this exact template