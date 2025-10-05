"""
Serializers for Locations API
Provides proper serialization and documentation for location endpoints
"""

from rest_framework import serializers
from .models import Province, District, Municipality


class ProvinceSerializer(serializers.ModelSerializer):
    """Serializer for Province model"""
    districts_count = serializers.IntegerField(source='districts.count', read_only=True)

    class Meta:
        model = Province
        fields = ['id', 'code', 'name_en', 'name_ne', 'districts_count']


class DistrictSerializer(serializers.ModelSerializer):
    """Serializer for District model"""
    province_name = serializers.CharField(source='province.name_en', read_only=True)
    municipalities_count = serializers.IntegerField(source='municipalities.count', read_only=True)

    class Meta:
        model = District
        fields = ['id', 'code', 'name_en', 'name_ne', 'province', 'province_name', 'municipalities_count']


class MunicipalitySerializer(serializers.ModelSerializer):
    """Serializer for Municipality model"""
    district_name = serializers.CharField(source='district.name_en', read_only=True)
    type_display = serializers.CharField(source='get_municipality_type_display', read_only=True)

    class Meta:
        model = Municipality
        fields = [
            'id',
            'code',
            'name_en',
            'name_ne',
            'district',
            'district_name',
            'municipality_type',
            'type_display',
            'total_wards'
        ]


class WardSerializer(serializers.Serializer):
    """Serializer for ward information"""
    ward_number = serializers.IntegerField()
    municipality = serializers.CharField()
    district = serializers.CharField()
    province = serializers.CharField()


class GeoResolveSerializer(serializers.Serializer):
    """Serializer for geolocation resolution"""
    lat = serializers.FloatField(required=True, help_text="Latitude coordinate")
    lng = serializers.FloatField(required=True, help_text="Longitude coordinate")


class GeoResolveResponseSerializer(serializers.Serializer):
    """Response serializer for geolocation resolution"""
    province = ProvinceSerializer(read_only=True)
    district = DistrictSerializer(read_only=True)
    municipality = MunicipalitySerializer(read_only=True)
    ward_number = serializers.IntegerField(allow_null=True)
    formatted_address = serializers.CharField()
    confidence_score = serializers.FloatField(help_text="Confidence level of the match (0-1)")


class LocationStatsSerializer(serializers.Serializer):
    """Serializer for location statistics"""
    total_provinces = serializers.IntegerField()
    total_districts = serializers.IntegerField()
    total_municipalities = serializers.IntegerField()
    total_wards = serializers.IntegerField()
    municipalities_by_type = serializers.DictField(child=serializers.IntegerField())
    last_updated = serializers.DateTimeField()