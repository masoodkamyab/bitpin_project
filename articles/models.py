from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class Article(models.Model):
    title = models.CharField(max_length=255)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    sum_ratings = models.FloatField(default=0)
    count_ratings = models.IntegerField(default=0)

    def update_average(self, new_ratings):
        if new_ratings:
            self.sum_ratings = sum(new_ratings)
            self.count_ratings = len(new_ratings)


class Rating(models.Model):
    article = models.ForeignKey(Article, related_name='ratings', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    score = models.PositiveSmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(5)])
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('article', 'user')
        indexes = [
            models.Index(fields=['article', 'user']),
        ]


class AccumulatedRating(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    score = models.PositiveSmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(5)])
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['article', 'user']),
        ]
