from django.db import models

from django.contrib.gis.db.models import PolygonField


class Leaflet(models.Model):
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
        verbose_name = "Map"
        verbose_name_plural = "Maps"
        unique_together = ['name', 'created_by']

    def __str__(self):
        return self.name


class LeafletMap(models.Model):
    geometry = PolygonField(
        blank=True,
        null=True
    )
    caption = models.CharField(
        blank=True,
        null=True,
        max_length=150
    )
    leaflet = models.ForeignKey(
        Leaflet,
        on_delete=models.CASCADE,
        related_name='leafletmaps'
    )
