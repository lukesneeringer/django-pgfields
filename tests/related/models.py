from django_pg import models


class Game(models.Model):
    label = models.CharField(max_length=100)
    number = models.PositiveIntegerField()
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)


class Moogle(models.Model):
    game = models.ForeignKey(Game)
    label = models.CharField(max_length=100)
    sex = models.CharField(max_length=1, choices=(
        ('m', 'Male'),
        ('f', 'Female'),
    ))
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        select_related = 'game'


class Letter(models.Model):
    game = models.ForeignKey(Game)
    moogle = models.ForeignKey(Moogle)
    addressee = models.CharField(max_length=20)
    sender = models.CharField(max_length=20)
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        select_related = ['game', 'moogle']
