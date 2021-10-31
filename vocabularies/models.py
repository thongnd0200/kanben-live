from django.db import models
from folders.models import Folders
# Create your models here.


class Vocabularies(models.Model):
    folders = models.ForeignKey(Folders, on_delete=models.CASCADE, null=True)
    vocabulary = models.CharField(max_length=50, null=True)
    definitions = models.JSONField(blank=True, null=True)
    reading = models.JSONField(blank=True, null=True)
                 
    def __str__(self) -> str:
        return self.vocabulary