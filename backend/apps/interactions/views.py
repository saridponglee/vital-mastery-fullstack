from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator
from apps.content.models import Article
from apps.content.events import event_publisher, counter_manager
from .models import Comment, Like, Bookmark
from .serializers import (
    CommentSerializer, CommentCreateSerializer,
    LikeSerializer, BookmarkSerializer
)
import logging

logger = logging.getLogger(__name__)


@method_decorator(ratelimit(key='user', rate='10/m', method='POST'), name='post')
class ArticleCommentsView(generics.ListCreateAPIView):
    """
    List and create comments for a specific article with real-time SSE events.
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
        ).select_related('author').prefetch_related('replies__author')
    
    def perform_create(self, serializer):
        """Create comment for the article and trigger real-time event."""
        article_slug = self.kwargs['article_slug']
        article = get_object_or_404(
            Article, 
            translations__slug=article_slug,
            status='published'
        )
        comment = serializer.save(article=article, author=self.request.user)
        
        # Real-time event will be triggered by Django signals
        logger.info(f"Comment created for article {article.id} by user {self.request.user.id}")
    
    def create(self, request, *args, **kwargs):
        """Override create to return enhanced response with real-time data."""
        response = super().create(request, *args, **kwargs)
        
        if response.status_code == status.HTTP_201_CREATED:
            # Add real-time statistics to response
            article_slug = self.kwargs['article_slug']
            article = get_object_or_404(
                Article, 
                translations__slug=article_slug,
                status='published'
            )
            
            response.data.update({
                'article_stats': {
                    'comments_count': counter_manager.get_article_comment_count(article.id),
                    'likes_count': counter_manager.get_article_like_count(article.id),
                    'views_count': counter_manager.get_article_views(article.id),
                }
            })
        
        return response


@api_view(['POST', 'DELETE'])
@permission_classes([permissions.IsAuthenticated])
@ratelimit(key='user', rate='20/m', method='POST')
@ratelimit(key='user', rate='20/m', method='DELETE')
def article_like_view(request, article_slug):
    """
    Like or unlike an article with real-time SSE events.
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
        
        # Get updated count from cache/counter manager
        likes_count = counter_manager.get_article_like_count(article.id)
        
        if created:
            logger.info(f"Article {article.id} liked by user {request.user.id}")
            return Response({
                'message': 'Article liked successfully',
                'liked': True,
                'likes_count': likes_count,
                'article_stats': {
                    'comments_count': counter_manager.get_article_comment_count(article.id),
                    'likes_count': likes_count,
                    'views_count': counter_manager.get_article_views(article.id),
                }
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'message': 'Article already liked',
                'liked': True,
                'likes_count': likes_count,
                'article_stats': {
                    'comments_count': counter_manager.get_article_comment_count(article.id),
                    'likes_count': likes_count,
                    'views_count': counter_manager.get_article_views(article.id),
                }
            }, status=status.HTTP_200_OK)
    
    elif request.method == 'DELETE':
        # Unlike the article
        try:
            like = Like.objects.get(article=article, user=request.user)
            like.delete()
            
            # Get updated count from cache/counter manager
            likes_count = counter_manager.get_article_like_count(article.id)
            
            logger.info(f"Article {article.id} unliked by user {request.user.id}")
            return Response({
                'message': 'Article unliked successfully',
                'liked': False,
                'likes_count': likes_count,
                'article_stats': {
                    'comments_count': counter_manager.get_article_comment_count(article.id),
                    'likes_count': likes_count,
                    'views_count': counter_manager.get_article_views(article.id),
                }
            }, status=status.HTTP_200_OK)
        except Like.DoesNotExist:
            likes_count = counter_manager.get_article_like_count(article.id)
            return Response({
                'message': 'Article was not liked',
                'liked': False,
                'likes_count': likes_count,
                'article_stats': {
                    'comments_count': counter_manager.get_article_comment_count(article.id),
                    'likes_count': likes_count,
                    'views_count': counter_manager.get_article_views(article.id),
                }
            }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
@ratelimit(key='ip', rate='60/m', method='GET')
def article_interactions_view(request, article_slug):
    """
    Get real-time interaction counts and statistics for an article.
    Uses cached counters for optimal performance.
    """
    article = get_object_or_404(
        Article, 
        translations__slug=article_slug,
        status='published'
    )
    
    # Use counter manager for optimized, cached counts
    data = {
        'likes_count': counter_manager.get_article_like_count(article.id),
        'comments_count': counter_manager.get_article_comment_count(article.id),
        'views_count': counter_manager.get_article_views(article.id),
        'article_id': article.id,
        'article_slug': article_slug,
    }
    
    # Add user-specific data if authenticated
    if request.user.is_authenticated:
        data.update({
            'user_liked': Like.objects.filter(article=article, user=request.user).exists(),
            'user_bookmarked': Bookmark.objects.filter(article=article, user=request.user).exists(),
        })
    else:
        data.update({
            'user_liked': False,
            'user_bookmarked': False,
        })
    
    return Response(data)


@api_view(['POST', 'DELETE'])
@permission_classes([permissions.IsAuthenticated])
@ratelimit(key='user', rate='15/m', method='POST')
@ratelimit(key='user', rate='15/m', method='DELETE')
def article_bookmark_view(request, article_slug):
    """
    Bookmark or remove bookmark from an article.
    """
    article = get_object_or_404(
        Article, 
        translations__slug=article_slug,
        status='published'
    )
    
    if request.method == 'POST':
        # Bookmark the article
        bookmark, created = Bookmark.objects.get_or_create(
            article=article,
            user=request.user
        )
        
        if created:
            logger.info(f"Article {article.id} bookmarked by user {request.user.id}")
            return Response({
                'message': 'Article bookmarked successfully',
                'bookmarked': True,
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'message': 'Article already bookmarked',
                'bookmarked': True,
            }, status=status.HTTP_200_OK)
    
    elif request.method == 'DELETE':
        # Remove bookmark
        try:
            bookmark = Bookmark.objects.get(article=article, user=request.user)
            bookmark.delete()
            
            logger.info(f"Article {article.id} bookmark removed by user {request.user.id}")
            return Response({
                'message': 'Bookmark removed successfully',
                'bookmarked': False,
            }, status=status.HTTP_200_OK)
        except Bookmark.DoesNotExist:
            return Response({
                'message': 'Article was not bookmarked',
                'bookmarked': False,
            }, status=status.HTTP_200_OK)