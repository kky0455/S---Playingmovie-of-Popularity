# articles/views.py

from django.shortcuts import get_object_or_404
from django.db.models import Count

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Movie, Comment
from .serializers.movie import MovieListSerializer, MovieSerializer
from .serializers.comment import CommentSerializer


@api_view(['GET', 'POST'])
def movie_list_or_create(request):

    def movie_list():
        # comment 개수 추가
        movies = Movie.objects.annotate(
            comment_count=Count('comments', distinct=True),
            like_count=Count('like_users', distinct=True)
        ).order_by('-pk')
        serializer = MovieListSerializer(movies, many=True)
        return Response(serializer.data)
    
    # def create_movie():
    #     serializer = MovieSerializer(data=request.data)
    #     if serializer.is_valid(raise_exception=True):
    #         serializer.save(user=request.user)
    #         return Response(serializer.data, status=status.HTTP_201_CREATED)

    if request.method == 'GET':
        return movie_list()
    # elif request.method == 'POST':
    #     return create_movie()


@api_view(['GET', 'PUT', 'DELETE'])
def movie_detail_or_update_or_delete(request, movie_pk):
    movie = get_object_or_404(Movie, pk=movie_pk)

    def movie_detail():
        serializer = MovieSerializer(movie)
        return Response(serializer.data)

    # def update_movie():
    #     if request.user == movie.user:
    #         serializer = MovieSerializer(instance=movie, data=request.data)
    #         if serializer.is_valid(raise_exception=True):
    #             serializer.save()
    #             return Response(serializer.data)

    # def delete_movie():
    #     if request.user == movie.user:
    #         movie.delete()
    #         return Response(status=status.HTTP_204_NO_CONTENT)

    if request.method == 'GET':
        return movie_detail()
    # elif request.method == 'PUT':
    #     if request.user == movie.user:
    #         return update_movie()
    # elif request.method == 'DELETE':
    #     if request.user == movie.user:
    #         return delete_movie()


@api_view(['POST'])
def like_movie(request, movie_pk):
    movie = get_object_or_404(Movie, pk=movie_pk)
    user = request.user
    if movie.like_users.filter(pk=user.pk).exists():
        movie.like_users.remove(user)
        serializer = MovieSerializer(movie)
        return Response(serializer.data)
    else:
        movie.like_users.add(user)
        serializer = MovieSerializer(movie)
        return Response(serializer.data)


@api_view(['POST'])
def create_comment(request, movie_pk):
    user = request.user
    movie = get_object_or_404(Movie, pk=movie_pk)
    
    serializer = CommentSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        serializer.save(movie=movie, user=user)

        # 기존 serializer 가 return 되면, 단일 comment 만 응답으로 받게됨.
        # 사용자가 댓글을 입력하는 사이에 업데이트된 comment 확인 불가 => 업데이트된 전체 목록 return 
        comments = movie.comments.all()
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['PUT', 'DELETE'])
def comment_update_or_delete(request, movie_pk, comment_pk):
    movie = get_object_or_404(Movie, pk=movie_pk)
    comment = get_object_or_404(Comment, pk=comment_pk)

    def update_comment():
        if request.user == comment.user:
            serializer = CommentSerializer(instance=comment, data=request.data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                comments = movie.comments.all()
                serializer = CommentSerializer(comments, many=True)
                return Response(serializer.data)
        data = {
            'update' : f'작성자만 수정할 수 있습니다.'
        }
        return Response(data, status=status.HTTP_304_NOT_MODIFIED)

    def delete_comment():
        if request.user == comment.user:
            comment.delete()
            comments = movie.comments.all()
            serializer = CommentSerializer(comments, many=True)
            return Response(serializer.data)
    
    if request.method == 'PUT':
        return update_comment()
    elif request.method == 'DELETE':
        return delete_comment()
