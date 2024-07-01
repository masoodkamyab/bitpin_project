from celery import shared_task
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from .models import Article, AccumulatedRating
from statistics import mean, stdev, median


@shared_task
def accumulate_rating(article_id, user_id, score):
    article = Article.objects.get(id=article_id)
    user = User.objects.get(id=user_id)
    AccumulatedRating.objects.create(article=article, user=user, score=score, timestamp=timezone.now())


@shared_task
def process_accumulated_ratings():
    cutoff_time = timezone.now() - timedelta(minutes=10)
    ratings_to_process = AccumulatedRating.objects.filter(timestamp__lte=cutoff_time)

    articles_to_process = ratings_to_process.values_list('article_id', flat=True).distinct()
    for article_id in articles_to_process:
        process_article_ratings(article_id)


@shared_task
def process_article_ratings(article_id):
    article = Article.objects.get(id=article_id)
    ratings = AccumulatedRating.objects.filter(article=article)
    scores = [rating.score for rating in ratings]

    if len(scores) >= 5:
        q1 = median([score for score in scores if score <= median(scores)])
        q3 = median([score for score in scores if score >= median(scores)])
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        filtered_scores = [score for score in scores if lower_bound <= score <= upper_bound]
    else:
        filtered_scores = scores

    article.update_average(filtered_scores)
    article.save()
    ratings.delete()

