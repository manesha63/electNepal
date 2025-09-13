from django.db import models

class Province(models.Model):
    name_en = models.CharField(max_length=100, unique=True)
    name_ne = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True)
    
    class Meta:
        ordering = ['code']
        indexes = [models.Index(fields=['code'])]
    
    def __str__(self):
        return self.name_en


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
        return f"{self.name_en}, {self.province.name_en}"


class Municipality(models.Model):
    MUNICIPALITY_TYPES = [
        ('metropolitan', 'Metropolitan City'),
        ('sub_metropolitan', 'Sub-Metropolitan City'),
        ('municipality', 'Municipality'),
        ('rural_municipality', 'Rural Municipality'),
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
        return f"{self.name_en} {self.get_municipality_type_display()}"
