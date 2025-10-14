from django.db import models
from django.utils.translation import gettext_lazy as _, get_language

class Province(models.Model):
    name_en = models.CharField(max_length=100, unique=True)
    name_ne = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True)

    class Meta:
        ordering = ['code']
        indexes = [models.Index(fields=['code'])]

    def __str__(self):
        """Return province name in current language (auto-detected from request)"""
        current_lang = get_language()
        return self.name_ne if current_lang == 'ne' else self.name_en


class District(models.Model):
    province = models.ForeignKey(Province, on_delete=models.CASCADE, related_name='districts')
    name_en = models.CharField(max_length=100)
    name_ne = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)

    class Meta:
        ordering = ['name_en']
        unique_together = [['province', 'name_en']]
        indexes = [
            models.Index(fields=['province', 'name_en']),
            models.Index(fields=['code'])
        ]

    def __str__(self):
        """Return district name in current language (auto-detected from request)"""
        current_lang = get_language()
        district_name = self.name_ne if current_lang == 'ne' else self.name_en
        province_name = self.province.name_ne if current_lang == 'ne' else self.province.name_en
        return f"{district_name}, {province_name}"


class Municipality(models.Model):
    MUNICIPALITY_TYPES = [
        ('metropolitan', _('Metropolitan City')),
        ('sub_metropolitan', _('Sub-Metropolitan City')),
        ('municipality', _('Municipality')),
        ('rural_municipality', _('Rural Municipality')),
    ]
    
    district = models.ForeignKey(District, on_delete=models.CASCADE, related_name='municipalities')
    name_en = models.CharField(max_length=100)
    name_ne = models.CharField(max_length=100)
    municipality_type = models.CharField(max_length=20, choices=MUNICIPALITY_TYPES)
    code = models.CharField(max_length=15, unique=True)
    total_wards = models.IntegerField(default=9)
    
    class Meta:
        ordering = ['name_en']
        unique_together = [['district', 'name_en']]
        indexes = [
            models.Index(fields=['district', 'municipality_type']),
            models.Index(fields=['code'])
        ]
        verbose_name_plural = 'Municipalities'

    def __str__(self):
        """Return municipality name in current language (auto-detected from request)"""
        current_lang = get_language()
        municipality_name = self.name_ne if current_lang == 'ne' else self.name_en
        return f"{municipality_name} {self.get_municipality_type_display()}"
