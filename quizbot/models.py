from django.db import models


class result(models.Model):
    name = models.CharField(max_length=100)
    topic = models.CharField(max_length=100)
    score = models.IntegerField()
    total = models.IntegerField()
    percent = models.IntegerField()
    grade = models.CharField(max_length=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} — {self.topic} — {self.score}/{self.total}"
