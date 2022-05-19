from rest_framework import serializers
from django.contrib.auth import get_user_model

from ..models import Movie
from .comment import CommentSerializer

User = get_user_model()

class MovieSerializer(serializers.ModelSerializer):
    
    class UserSerializer(serializers.ModelSerializer):
        class Meta:
            model = User
            fields = ('pk', 'username')

    comments = CommentSerializer(many=True, read_only=True)
    user = UserSerializer(read_only=True)
    like_users = UserSerializer(read_only=True, many=True)

    class Meta:
        model = Movie
        fields = ('pk', 'user', 'title', 'original_title', 'comments', 'like_users', 'overview', 'release_date', 'poster_path', 'vote_average', 'genre', 'like_user')


# Article List Read
class MovieListSerializer(serializers.ModelSerializer):
    class UserSerializer(serializers.ModelSerializer):
        class Meta:
            model = User
            fields = ('pk', 'username')

    user = UserSerializer(read_only=True)
    # queryset annotate (views에서 채워줄것!)
    comment_count = serializers.IntegerField()
    like_count = serializers.IntegerField()

    class Meta:
        model = Movie
        fields = ('pk', 'user', 'title', 'comment_count', 'like_count')
