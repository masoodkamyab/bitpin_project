from rest_framework import serializers
from .models import Article, Rating


class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ['score']

    def validate_score(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Score must be between 1 and 5.")
        return value


class ArticleSerializer(serializers.ModelSerializer):
    average_rating = serializers.FloatField(read_only=True)
    num_ratings = serializers.IntegerField(read_only=True)
    user_rating = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = ['id', 'title', 'text', 'average_rating', 'num_ratings', 'user_rating']

    def get_user_rating(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            rating = obj.ratings.filter(user=request.user).first()
            if rating:
                return rating.score
        return None
