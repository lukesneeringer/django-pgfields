from __future__ import absolute_import, unicode_literals
from django_pg import models


class Book(models.Model):
    title = models.CharField(max_length=50)
    year_published = models.IntegerField()


class Movie(models.Model):
    title = models.CharField(max_length=50)
    based_on = models.ForeignKey(Book, null=True)
    year_published = models.IntegerField()


class Publisher(models.Model):
    name = models.CharField(max_length=50)
    books = models.ManyToManyField(Book)


class Character(models.Model):
    name = models.CharField(max_length=50)
    enemy = models.ForeignKey('self', related_name='enemy_of', null=True)


class Interview(models.Model):
    subject = models.CharField(max_length=50)
    role = models.CharField(max_length=50)
    movie = models.ForeignKey(Movie)
    on_dvd = models.BooleanField(default=True)
    on_blu_ray = models.BooleanField(default=True)

    class Meta:
        repr_fields_exclude = ('on_dvd', 'on_blu_ray')


class Studio(models.Model):
    name = models.CharField(max_length=50)
    net_worth = models.PositiveIntegerField()

    class Meta:
        repr_fields = ('name',)
