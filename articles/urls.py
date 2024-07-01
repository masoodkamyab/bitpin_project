from django.urls import path
from .views import ArticleListView, RateArticleView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('articles/', ArticleListView.as_view(), name='article-list'),
    path('articles/<int:pk>/rate/', RateArticleView.as_view(), name='rate-article'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
