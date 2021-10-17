from django.db import models
from django.db.models.deletion import CASCADE
from folders.models import Folders
# Create your models here.


class Vocabularies(models.Model):
    folders = models.ForeignKey(Folders, on_delete=CASCADE, null=True)
    vocabulary = models.CharField(max_length=50, null=True)
    meaning = models.CharField(max_length=50, null=True)
    hiragana = models.CharField(max_length=50, null=True)

    def __str__(self) -> str:
        return self.vocabulary