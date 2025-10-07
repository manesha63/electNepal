"""
Serializers for Candidates API
Provides proper serialization and documentation for API endpoints
"""

from rest_framework import serializers
from .models import Candidate, CandidateEvent
from locations.models import Province, District, Municipality


class CandidateCardSerializer(serializers.ModelSerializer):
    """
    Serializer for candidate cards displayed in the feed.
    Returns minimal information needed for card display.
    """
    # Location names
    province_name = serializers.CharField(source='province.name_en', read_only=True)
    district_name = serializers.CharField(source='district.name_en', read_only=True)
    municipality_name = serializers.CharField(source='municipality.name_en', read_only=True, allow_null=True)

    # Template-compatible aliases
    name = serializers.CharField(source='full_name', read_only=True)
    photo = serializers.SerializerMethodField()
    photo_url = serializers.SerializerMethodField()
    detail_url = serializers.SerializerMethodField()
    office = serializers.SerializerMethodField()

    # Display fields
    position_display = serializers.CharField(source='get_position_level_display', read_only=True)
    location = serializers.SerializerMethodField()
    status_color = serializers.SerializerMethodField()

    # Location fields for template
    province = serializers.CharField(source='province.name_en', read_only=True)
    district = serializers.CharField(source='district.name_en', read_only=True)
    municipality = serializers.CharField(source='municipality.name_en', read_only=True, allow_null=True)
    ward = serializers.IntegerField(source='ward_number', read_only=True)

    class Meta:
        model = Candidate
        fields = [
            'id',
            'full_name',
            'name',
            'bio_en',
            'bio_ne',
            'position_level',
            'position_display',
            'photo',
            'photo_url',
            'detail_url',
            'office',
            'status',
            'status_color',
            'province',
            'province_name',
            'district',
            'district_name',
            'municipality',
            'municipality_name',
            'ward',
            'ward_number',
            'location',
            'created_at'
        ]

    def get_photo(self, obj):
        """Get the full URL for the candidate's photo (alias for photo_url)"""
        return self.get_photo_url(obj)

    def get_photo_url(self, obj):
        """Get the full URL for the candidate's photo"""
        from django.conf import settings
        request = self.context.get('request')
        if obj.photo and request:
            return request.build_absolute_uri(obj.photo.url)
        # Return default avatar if no photo
        if request:
            return request.build_absolute_uri(settings.DEFAULT_CANDIDATE_AVATAR)
        return settings.DEFAULT_CANDIDATE_AVATAR

    def get_detail_url(self, obj):
        """Get the candidate detail page URL"""
        from django.urls import reverse
        return reverse('candidates:detail', kwargs={'pk': obj.id})

    def get_office(self, obj):
        """Get office level based on position"""
        # Map position_level to office
        position_to_office = {
            'ward_chairperson': 'ward',
            'ward_member': 'ward',
            'mayor_chairperson': 'municipal',
            'deputy_mayor_vice_chairperson': 'municipal',
            'provincial_assembly': 'provincial',
            'house_of_representatives': 'federal',
            'national_assembly': 'federal',
        }
        return position_to_office.get(obj.position_level, 'municipal')

    def get_location(self, obj):
        """Format location as a single string"""
        parts = []
        if obj.ward_number:
            parts.append(f"Ward {obj.ward_number}")
        if obj.municipality:
            parts.append(obj.municipality.name_en)
        parts.append(obj.district.name_en)
        parts.append(obj.province.name_en)
        return ", ".join(parts)

    def get_status_color(self, obj):
        """Return color code for status badge"""
        return {
            'pending': 'orange',
            'approved': 'green',
            'rejected': 'red'
        }.get(obj.status, 'gray')


class CandidateBallotSerializer(serializers.ModelSerializer):
    """
    Serializer for ballot view.
    Returns candidates with relevance scoring based on location.
    """
    province_name = serializers.CharField(source='province.name_en', read_only=True)
    district_name = serializers.CharField(source='district.name_en', read_only=True)
    municipality_name = serializers.CharField(source='municipality.name_en', read_only=True, allow_null=True)
    photo_url = serializers.SerializerMethodField()
    relevance_score = serializers.IntegerField(read_only=True, help_text="Location match score (higher is better)")
    location_match = serializers.CharField(read_only=True, help_text="Type of location match")

    class Meta:
        model = Candidate
        fields = [
            'id',
            'full_name',
            'bio_en',
            'bio_ne',
            'position_level',
            'photo_url',
            'province_name',
            'district_name',
            'municipality_name',
            'ward_number',
            'relevance_score',
            'location_match'
        ]

    def get_photo_url(self, obj):
        from django.conf import settings
        request = self.context.get('request')
        if obj.photo and request:
            return request.build_absolute_uri(obj.photo.url)
        # Return default avatar if no photo
        if request:
            return request.build_absolute_uri(settings.DEFAULT_CANDIDATE_AVATAR)
        return settings.DEFAULT_CANDIDATE_AVATAR


class LocationFilterSerializer(serializers.Serializer):
    """Serializer for location filter parameters"""
    province_id = serializers.IntegerField(required=False, help_text="Province ID to filter by")
    district_id = serializers.IntegerField(required=False, help_text="District ID to filter by")
    municipality_id = serializers.IntegerField(required=False, help_text="Municipality ID to filter by")
    ward_number = serializers.IntegerField(required=False, help_text="Ward number to filter by")


class PaginationSerializer(serializers.Serializer):
    """Serializer for pagination parameters"""
    page = serializers.IntegerField(required=False, default=1, help_text="Page number")
    page_size = serializers.IntegerField(required=False, default=20, help_text="Number of items per page (max: 100)")


class SearchSerializer(serializers.Serializer):
    """Serializer for search parameters"""
    q = serializers.CharField(required=False, help_text="Search query string")
    province = serializers.IntegerField(required=False, help_text="Filter by province ID")
    district = serializers.IntegerField(required=False, help_text="Filter by district ID")
    municipality = serializers.IntegerField(required=False, help_text="Filter by municipality ID")
    position = serializers.ChoiceField(
        required=False,
        choices=[
            ('federal', 'Federal'),
            ('provincial', 'Provincial'),
            ('mayor', 'Mayor'),
            ('deputy_mayor', 'Deputy Mayor'),
            ('ward', 'Ward Chairperson'),
            ('ward_member', 'Ward Member'),
            ('womens_member', "Women's Member"),
            ('dalit_womens_member', "Dalit Women's Member"),
            ('local_executive', 'Local Executive'),
        ],
        help_text="Filter by position level"
    )