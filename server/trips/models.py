from django.db import models


class City(models.Model):
    name        = models.CharField(max_length=255)
    population  = models.PositiveIntegerField()

    class Meta:
        verbose_name = 'City'
        verbose_name_plural = 'Cities'

        ordering = ('name', )

