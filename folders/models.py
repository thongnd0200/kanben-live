from os import name
from django.db import models
from django.db.models.deletion import CASCADE
from accounts.models import User
from django.db.models.fields.related import ForeignKey


# Create your models here.


class Folders(models.Model):
    user = models.ForeignKey(User, on_delete=CASCADE, null=True)
    name = models.CharField(max_length=50, null=True)
    visibility = models.BooleanField(default=False, null=True)
    result = models.IntegerField(null=True)


    def __str__(self) -> str:
        return self.name
    
    @property
    def get_vocabularies(self):
        all_vocabularies = self.vocabularies_set.all()
        return all_vocabularies
    
    @property
    def get_id_vocabularies(self):  
        all_vocabularies = self.vocabularies_set.all()
        all_id_vocabularies = [item.id for item in all_vocabularies]
        return all_id_vocabularies

    @property
    def total_vocabularies(self):  
        all_vocabularies = self.vocabularies_set.all()
        return len(all_vocabularies)