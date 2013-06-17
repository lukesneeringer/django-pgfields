from django_pg import models


class MonarchField(models.CompositeField):
    title = models.CharField(max_length=20)
    name = models.CharField(max_length=50)
    suffix = models.IntegerField(default=0)


class BookField(models.CompositeField):
    title = models.CharField(max_length=100)
    pages = models.IntegerField()


class ItemField(models.CompositeField):
    name = models.CharField(max_length=50)
    acquired_in = BookField()
