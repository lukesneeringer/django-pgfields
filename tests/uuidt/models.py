from django_pg import models


class Movie(models.Model):
    id = models.UUIDField(auto_add=True, primary_key=True)
    title = models.CharField(max_length=50)


class Game(models.Model):
    title = models.CharField(max_length=50)
    uuid = models.UUIDField()


class Book(models.Model):
    title = models.CharField(max_length=50)
    uuid = models.UUIDField(null=True)
