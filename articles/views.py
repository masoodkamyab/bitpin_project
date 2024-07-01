from drf_spectacular.utils import extend_schema, OpenApiParameter, extend_schema_view
from rest_framework import generics, status
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.db.models import Avg, Count
from .models import Article, Rating
from .serializers import ArticleSerializer, RatingSerializer
from .tasks import accumulate_rating


class ArticlePagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


@extend_schema_view(
    get=extend_schema(
        tags=['Articles'],
        parameters=[
            OpenApiParameter(name='ordering', description='Ordering', required=False, type=str),
            OpenApiParameter(name='search', description='Search', required=False, type=str),
        ],
    ),
)
class ArticleListView(generics.ListAPIView):
    queryset = Article.objects.annotate(
        average_rating=Avg('ratings__score'),
        num_ratings=Count('ratings')
    ).order_by('-created_at')
    serializer_class = ArticleSerializer
    pagination_class = ArticlePagination
    permission_classes = [IsAuthenticatedOrReadOnly]
    authentication_classes = [JWTAuthentication]
    search_fields = ['title', 'text']
    filter_backends = [OrderingFilter, SearchFilter]
    ordering_fields = ['id', 'title', 'average_rating', 'num_ratings']
    ordering = ['-id']

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context


@extend_schema_view(
    post=extend_schema(
        tags=['Ratings'],
    )
)
class RateArticleView(APIView):
    serializer_class = RatingSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request, pk):
        article = Article.objects.get(id=pk)
        user = request.user

        serializer = RatingSerializer(data=request.data)
        if serializer.is_valid():
            score = serializer.validated_data['score']
            accumulate_rating.delay(article.id, user.id, score)
            return Response({'status': 'rating set'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
