from datetime import timedelta
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import User
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Article, AccumulatedRating
from .tasks import process_accumulated_ratings


class ArticleTests(APITestCase):
    def setUp(self):
        # Create a user and authenticate using JWT
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client = APIClient()
        self.client.login(username='testuser', password='password')

        # Obtain the JWT token
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        # Create articles
        self.article1 = Article.objects.create(title="Test Article 1", text="Content for test article 1")
        self.article2 = Article.objects.create(title="Test Article 2", text="Content for test article 2")

        # Endpoint URLs
        self.article_list_url = reverse('article-list')
        self.rate_article_url = lambda pk: reverse('rate-article', kwargs={'pk': pk})

    def test_list_articles(self):
        # Test listing articles
        response = self.client.get(self.article_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titles = [article['title'] for article in response.data['results']]
        self.assertIn("Test Article 1", titles)
        self.assertIn("Test Article 2", titles)

    def test_accumulate_rating(self):
        # Test accumulating a rating
        rate_data = {'score': 4}
        response = self.client.post(self.rate_article_url(self.article1.id), rate_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check if the rating is accumulated
        accumulated_rating = AccumulatedRating.objects.get(article=self.article1, user=self.user)
        self.assertEqual(accumulated_rating.score, 4)

    def test_process_accumulated_ratings(self):
        # Accumulate ratings with some variance
        ratings = [1, 2, 2, 2, 2, 5]  # Most ratings are similar, but 1 and 5 are outliers
        for score in ratings:
            rate_data = {'score': score}
            self.client.post(self.rate_article_url(self.article1.id), rate_data, format='json')

        # Ensure accumulated ratings have a timestamp older than 10 minutes
        AccumulatedRating.objects.update(timestamp=timezone.now() - timedelta(minutes=15))

        # Run the task to process accumulated ratings
        process_accumulated_ratings()

        self.article1.refresh_from_db()

        # Print debugging information
        print(f"Sum ratings: {self.article1.sum_ratings}")
        print(f"Count ratings: {self.article1.count_ratings}")

        # Validate statistics after processing
        self.assertEqual(self.article1.count_ratings, 4)
        self.assertTrue(self.article1.sum_ratings <= 14)
        self.assertTrue(2 <= self.article1.sum_ratings / self.article1.count_ratings <= 3)


class PerformanceTests(APITestCase):
    def setUp(self):
        # Create a user and authenticate using JWT
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client = APIClient()
        self.client.login(username='testuser', password='password')

        # Obtain the JWT token
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        # Create an article
        self.article = Article.objects.create(title="Performance Test Article", text="Content for performance test article")

        # Endpoint URLs
        self.rate_article_url = reverse('rate-article', kwargs={'pk': self.article.id})

    def test_massive_ratings(self):
        # Simulate 1000 users rating the article with a mix of realistic and unrealistic ratings
        realistic_ratings = [2] * 400 + [3] * 400  # 800 ratings of 2, 3
        unrealistic_ratings = [1, 5] * 100  # 100 ratings of 1 and 100 ratings of 5

        # Combine all ratings
        all_ratings = realistic_ratings + unrealistic_ratings

        # Create 1000 users and submit their ratings
        for i, score in enumerate(all_ratings):
            user = User.objects.create_user(username=f'user{i}', password='password')
            rate_data = {'score': score}
            self.client.post(self.rate_article_url, rate_data, format='json')

        # Ensure accumulated ratings have a timestamp older than 10 minutes
        AccumulatedRating.objects.update(timestamp=timezone.now() - timedelta(minutes=15))

        # Run the task to process accumulated ratings
        process_accumulated_ratings()

        self.article.refresh_from_db()

        # Print debugging information
        print(f"Sum ratings: {self.article.sum_ratings}")
        print(f"Count ratings: {self.article.count_ratings}")
        print(f"Moving average: {self.article.sum_ratings / self.article.count_ratings}")
        self.assertTrue(2 <= self.article.sum_ratings / self.article.count_ratings <= 3)


if __name__ == '__main__':
    import unittest

    unittest.main()
