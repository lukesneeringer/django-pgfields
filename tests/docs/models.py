from django_pg import models


class Hobbit(models.Model):
    name = models.CharField(max_length=50)
    favorite_foods = models.ArrayField(models.CharField(max_length=100))
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)


class Elf(models.Model):
    id = models.UUIDField(auto_add=True, primary_key=True)
    name = models.CharField(max_length=50)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)


class AuthorField(models.CompositeField):
    name = models.CharField(max_length=75)
    sex = models.CharField(max_length=6, choices=(
        ('male', 'Male'),
        ('female', 'Female'),
    ))
    birthdate = models.DateField()


class Book(models.Model):
    title = models.CharField(max_length=50)
    author = AuthorField()
    date_published = models.DateField()
