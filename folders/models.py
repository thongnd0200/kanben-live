from django.db import models
from accounts.models import User

# Create your models here.
class Topic(models.Model):
    topic_name = models.CharField(max_length=100, null=True)

    def __str__(self) -> str:
        return self.topic_name


class Folders(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=50, null=True)
    visibility = models.BooleanField(default=True, null=True)
    result = models.IntegerField(null=True)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, null=True)

    def __str__(self) -> str:
        return self.name

    def author_id(self):
        if self.user:
            return self.user.id
        return None

    def author_name(self):
        if self.user:
            return self.user.username
        return None

    def topic_name(self):
        if self.topic:
            return self.topic.topic_name
        return None
    
    def list_vocabularies(self):
        all_vocabularies = self.vocabularies_set.all().values()
        return [dict(vocabulary) for vocabulary in all_vocabularies]
    
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