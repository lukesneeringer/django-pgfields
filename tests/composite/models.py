from django_pg import models
from tests.composite import fields


class Monarchy(models.Model):
    name = models.CharField(max_length=100)
    ruler = fields.MonarchField()


class Author(models.Model):
    name = models.CharField(max_length=100)
    sex = models.CharField(max_length=6, choices=(
        ('male', 'Male'),
        ('female', 'Female'),
    ))
    birthday = models.DateField()
    books = models.ArrayField(of=fields.BookField)


class Character(models.Model):
    name = models.CharField(max_length=50)
    items = models.ArrayField(of=fields.ItemField)
