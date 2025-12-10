from django.db import models

from django.contrib.gis.db.models import PolygonField


class Region(models.Model):
    name = models.CharField(
        verbose_name="Geometry name",
        max_length=50,
    )
    created_by = models.CharField(
        editable=False,
        max_length=40,
        db_index=True,
    )

    class Meta:
        verbose_name = "Region"
        verbose_name_plural = "Regions"
        unique_together = ['name', 'created_by']

    def __str__(self):
        return self.name


class RegionMap(models.Model):
    geometry = PolygonField(
        blank=True,
        null=True
    )
    caption = models.CharField(
        blank=True,
        null=True,
        max_length=150
    )
    region = models.ForeignKey(
        Region,
        on_delete=models.CASCADE,
        related_name='regionmaps'
    )
