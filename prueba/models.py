from django.db import models
from accounts.models import Role, CustomUser


class Topic(models.Model):
    name = models.CharField(max_length=255)
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='topics')

    def __str__(self):
        return self.name


class Question(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    text = models.TextField()

    def __str__(self):
        return self.text


class Option(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    text = models.CharField(max_length=255)
    score = models.IntegerField(default=1)

    def __str__(self):
        return self.text


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    option = models.ForeignKey(Option, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.email} - {self.question.text}"


class TopicResult(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    score = models.FloatField(default=0)
    level = models.CharField(max_length=10, default='A1')
    total_questions = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.topic.name} - {self.user.email}"


from django.db import models

# Create your models here.
