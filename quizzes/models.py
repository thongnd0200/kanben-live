from django.db import models
from django.db.models.deletion import CASCADE
from folders.models import Folders
from itertools import permutations
import random

# Create your models here.


class Quizzes(models.Model):
    folder = models.ForeignKey(Folders, on_delete=CASCADE)
    question = models.CharField(max_length=50)
    answer = models.CharField(max_length=50)

    def __str__(self) -> str:
        return self.question

    @property
    def random_opt(self, answer, opt):
        folder_vocabularies = self.folder.total_vocabularies()
        options_list = [answer.id]
        while len(options_list) < 4:
            temp = random.randint(folder_vocabularies)
            if temp not in options_list:
                options_list.append(temp)
        return options_list
    
    @property
    def random_opt_showed(self):
        perm = permutations(self.random_opt())
        total_perm = len([item for item in perm])
        showed = random.randint(1, total_perm)
        return showed