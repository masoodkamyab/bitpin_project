from django.contrib import admin
from .models import Article, Rating


class RatingInline(admin.TabularInline):
    model = Rating
    extra = 1


class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'get_average_rating', 'count_ratings', 'created_at', 'updated_at')
    inlines = [RatingInline]

    def get_average_rating(self, obj):
        return obj.sum_ratings / obj.count_ratings
    get_average_rating.short_description = 'Average Rating'


admin.site.register(Article, ArticleAdmin)
admin.site.register(Rating)
