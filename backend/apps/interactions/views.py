from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from apps.content.models import Article
from .models import Comment, Like, Bookmark
from .serializers import (
    CommentSerializer, CommentCreateSerializer,
    LikeSerializer, BookmarkSerializer
)


class ArticleCommentsView(generics.ListCreateAPIView):
    """
    List and create comments for a specific article.
    """
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CommentCreateSerializer
        return CommentSerializer
    
    def get_queryset(self):
        """Get approved comments for the article."""
        article_slug = self.kwargs['article_slug']
        return Comment.objects.filter(
            article__translations__slug=article_slug,
            is_approved=True,
            parent=None  # Only top-level comments
        ).select_related('author').prefetch_related('replies')
    
    def perform_create(self, serializer):
        """Create comment for the article."""
        article_slug = self.kwargs['article_slug']
        article = get_object_or_404(
            Article, 
            translations__slug=article_slug,
            status='published'
        )
        serializer.save(article=article, author=self.request.user)


@api_view(['POST', 'DELETE'])
@permission_classes([permissions.IsAuthenticated])
def article_like_view(request, article_slug):
    """
    Like or unlike an article.
    """
    article = get_object_or_404(
        Article, 
        translations__slug=article_slug,
        status='published'
    )
    
    if request.method == 'POST':
        # Like the article
        like, created = Like.objects.get_or_create(
            article=article,
            user=request.user
        )
        
        if created:
            return Response({
                'message': 'Article liked successfully',
                'liked': True,
                'likes_count': article.likes.count()
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'message': 'Article already liked',
                'liked': True,
                'likes_count': article.likes.count()
            }, status=status.HTTP_200_OK)
    
    elif request.method == 'DELETE':
        # Unlike the article
        try:
            like = Like.objects.get(article=article, user=request.user)
            like.delete()
            return Response({
                'message': 'Article unliked successfully',
                'liked': False,
                'likes_count': article.likes.count()
            }, status=status.HTTP_200_OK)
        except Like.DoesNotExist:
            return Response({
                'message': 'Article was not liked',
                'liked': False,
                'likes_count': article.likes.count()
            }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def article_interactions_view(request, article_slug):
    """
    Get interaction counts for an article.
    """
    article = get_object_or_404(
        Article, 
        translations__slug=article_slug,
        status='published'
    )
    
    data = {
        'likes_count': article.likes.count(),
        'comments_count': article.comments.filter(is_approved=True).count(),
    }
    
    # Add user-specific data if authenticated
    if request.user.is_authenticated:
        data.update({
            'user_liked': article.likes.filter(user=request.user).exists(),
        })
    else:
        data.update({
            'user_liked': False,
        })
    
    return Response(data)