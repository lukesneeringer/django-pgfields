from django_pg import models


class Song(models.Model):
    title = models.CharField(max_length=50)
    data = models.JSONField()
    sample_lines = models.JSONField(default=[])
    stuff = models.JSONField(default=None)
