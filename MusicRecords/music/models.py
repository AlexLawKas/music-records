from django.db import models

# Create your models here.
from django.db import models


class Performer(models.Model):
    """Исполнитель"""
    name = models.CharField(max_length=100, unique=True)
    genre = models.CharField(max_length=100, null=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('name',)


class Records(models.Model):
    """Пластинки/АЛьбомы"""
    title = models.CharField(max_length=100)
    year = models.IntegerField(null=True)
    performer = models.ForeignKey(Performer, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ('title',)


class Songs(models.Model):
    """Песни"""
    title = models.CharField(max_length=100)
    records = models.ManyToManyField(Records, blank=True)
    performer = models.ForeignKey(Performer, on_delete=models.CASCADE)
    year = models.IntegerField(null=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ('title',)
