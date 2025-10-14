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
    Optimized to reduce payload size by removing unused fields.
    Language-aware: Returns location names in the current request language.
    """
    # Template-compatible aliases
    name = serializers.CharField(source='full_name', read_only=True)
    photo = serializers.SerializerMethodField()
    detail_url = serializers.SerializerMethodField()

    # Location fields for template (language-aware, no hardcoding)
    province = serializers.SerializerMethodField()
    district = serializers.SerializerMethodField()
    municipality = serializers.SerializerMethodField()
    ward = serializers.IntegerField(source='ward_number', read_only=True)

    class Meta:
        model = Candidate
        fields = [
            'id',
            'full_name',
            'name',
            'position_level',
            'photo',
            'detail_url',
            'province',
            'district',
            'municipality',
            'ward',
            'ward_number',
        ]

    def get_photo(self, obj):
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

    def get_province(self, obj):
        """Get province name in current language (auto-detected from request)"""
        if not obj.province:
            return None
        from django.utils.translation import get_language
        current_lang = get_language()
        return obj.province.name_ne if current_lang == 'ne' else obj.province.name_en

    def get_district(self, obj):
        """Get district name in current language (auto-detected from request)"""
        if not obj.district:
            return None
        from django.utils.translation import get_language
        current_lang = get_language()
        return obj.district.name_ne if current_lang == 'ne' else obj.district.name_en

    def get_municipality(self, obj):
        """Get municipality name in current language (auto-detected from request)"""
        if not obj.municipality:
            return None
        from django.utils.translation import get_language
        current_lang = get_language()
        return obj.municipality.name_ne if current_lang == 'ne' else obj.municipality.name_en


class CandidateBallotSerializer(serializers.ModelSerializer):
    """
    Serializer for ballot view.
    Returns candidates with relevance scoring based on location.
    Optimized to reduce payload size by removing unused fields.
    Language-aware: Returns location names in the current request language.
    """
    # Template-compatible aliases
    name = serializers.CharField(source='full_name', read_only=True)
    photo = serializers.SerializerMethodField()
    detail_url = serializers.SerializerMethodField()

    # Location fields for template (language-aware, no hardcoding)
    province = serializers.SerializerMethodField()
    district = serializers.SerializerMethodField()
    municipality = serializers.SerializerMethodField()
    ward = serializers.IntegerField(source='ward_number', read_only=True)

    class Meta:
        model = Candidate
        fields = [
            'id',
            'full_name',
            'name',
            'position_level',
            'photo',
            'detail_url',
            'province',
            'district',
            'municipality',
            'ward',
            'ward_number',
        ]

    def get_photo(self, obj):
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

    def get_province(self, obj):
        """Get province name in current language (auto-detected from request)"""
        if not obj.province:
            return None
        from django.utils.translation import get_language
        current_lang = get_language()
        return obj.province.name_ne if current_lang == 'ne' else obj.province.name_en

    def get_district(self, obj):
        """Get district name in current language (auto-detected from request)"""
        if not obj.district:
            return None
        from django.utils.translation import get_language
        current_lang = get_language()
        return obj.district.name_ne if current_lang == 'ne' else obj.district.name_en

    def get_municipality(self, obj):
        """Get municipality name in current language (auto-detected from request)"""
        if not obj.municipality:
            return None
        from django.utils.translation import get_language
        current_lang = get_language()
        return obj.municipality.name_ne if current_lang == 'ne' else obj.municipality.name_en


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