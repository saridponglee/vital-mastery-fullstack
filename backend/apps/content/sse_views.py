"""
Server-Sent Events (SSE) views with authentication and security.
Implements comprehensive SSE endpoints with rate limiting and permission checks.
"""

import json
import logging
from typing import Optional, List
from django.http import StreamingHttpResponse, HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from django.conf import settings
from django_ratelimit.decorators import ratelimit
from django_eventstream import get_current_event_id
from django_eventstream.views import events
from .channels import ChannelManager
from .events import counter_manager, editing_manager
import django_eventstream

logger = logging.getLogger(__name__)


class SSEPermissionMixin:
    """
    Mixin for SSE views with permission checking and rate limiting.
    """
    
    def check_sse_permission(self, request, channel: str) -> bool:
        """Check if user has permission to access SSE channel."""
        return ChannelManager.check_channel_permission(request.user, channel)
    
    def check_rate_limit(self, request, channel: str) -> bool:
        """Check and track connection rate limits."""
        user_id = request.user.id if request.user.is_authenticated else None
        return ChannelManager.track_connection(user_id, channel)


@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(ratelimit(key='ip', rate='10/m', method='GET'), name='dispatch')
class ArticleSSEView(SSEPermissionMixin, View):
    """
    SSE endpoint for article-specific real-time updates.
    Streams events for comments, likes, views, and article changes.
    """
    
    def get(self, request, article_id: int):
        """Stream SSE events for a specific article."""
        try:
            # Validate article exists
            from .models import Article
            try:
                article = Article.objects.get(id=article_id, status='published')
            except Article.DoesNotExist:
                return JsonResponse({'error': 'Article not found'}, status=404)
            
            # Get all article channels
            channels = ChannelManager.get_article_channels(article_id)
            
            # Check permissions for each channel
            allowed_channels = []
            for channel in channels:
                if self.check_sse_permission(request, channel):
                    if self.check_rate_limit(request, channel):
                        allowed_channels.append(channel)
                    else:
                        return JsonResponse({'error': 'Rate limit exceeded'}, status=429)
            
            if not allowed_channels:
                return JsonResponse({'error': 'Access denied'}, status=403)
            
            # Use django-eventstream's events for multiple channels
            return events(request, channels=allowed_channels)
            
        except Exception as e:
            logger.error(f"Error in ArticleSSEView: {str(e)}")
            return JsonResponse({'error': 'Internal server error'}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(ratelimit(key='ip', rate='5/m', method='GET'), name='dispatch')
class UserSSEView(SSEPermissionMixin, View):
    """
    SSE endpoint for user-specific notifications and updates.
    Requires authentication and only streams to the authenticated user.
    """
    
    @method_decorator(login_required)
    def get(self, request):
        """Stream SSE events for the authenticated user."""
        try:
            user_channels = ChannelManager.get_user_channels(request.user.id)
            
            # Check rate limits
            for channel in user_channels:
                if not self.check_rate_limit(request, channel):
                    return JsonResponse({'error': 'Rate limit exceeded'}, status=429)
            
            return events(request, channels=user_channels)
            
        except Exception as e:
            logger.error(f"Error in UserSSEView: {str(e)}")
            return JsonResponse({'error': 'Internal server error'}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(ratelimit(key='ip', rate='20/m', method='GET'), name='dispatch')
class GlobalSSEView(SSEPermissionMixin, View):
    """
    SSE endpoint for global notifications and announcements.
    Public endpoint with rate limiting.
    """
    
    def get(self, request):
        """Stream global SSE events."""
        try:
            channels = [
                ChannelManager.get_global_channel("notifications"),
                ChannelManager.get_global_channel("announcements"),
            ]
            
            # Check permissions and rate limits
            allowed_channels = []
            for channel in channels:
                if self.check_sse_permission(request, channel):
                    if self.check_rate_limit(request, channel):
                        allowed_channels.append(channel)
                    else:
                        return JsonResponse({'error': 'Rate limit exceeded'}, status=429)
            
            return events(request, channels=allowed_channels)
            
        except Exception as e:
            logger.error(f"Error in GlobalSSEView: {str(e)}")
            return JsonResponse({'error': 'Internal server error'}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(ratelimit(key='user', rate='3/m', method='GET'), name='dispatch')
class EditingSSEView(SSEPermissionMixin, View):
    """
    SSE endpoint for collaborative editing features.
    Requires authentication and edit permissions.
    """
    
    @method_decorator(login_required)
    def get(self, request, article_id: int):
        """Stream collaborative editing events."""
        try:
            # Validate article and permissions
            from .models import Article
            try:
                article = Article.objects.get(id=article_id)
            except Article.DoesNotExist:
                return JsonResponse({'error': 'Article not found'}, status=404)
            
            # Check edit permissions
            if not (article.author == request.user or request.user.is_staff):
                return JsonResponse({'error': 'Edit permission required'}, status=403)
            
            channel = ChannelManager.get_article_editing_channel(article_id)
            
            if not self.check_rate_limit(request, channel):
                return JsonResponse({'error': 'Rate limit exceeded'}, status=429)
            
            return events(request, channels=[channel])
            
        except Exception as e:
            logger.error(f"Error in EditingSSEView: {str(e)}")
            return JsonResponse({'error': 'Internal server error'}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@ratelimit(key='user', rate='30/m', method='POST')
def increment_view_count(request, article_id: int):
    """
    Increment article view count and broadcast update.
    Rate limited to prevent abuse.
    """
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
        
    try:
        from .models import Article
        article = Article.objects.get(id=article_id, status='published')
        
        # Increment view count atomically
        new_count = counter_manager.increment_article_views(article)
        
        return JsonResponse({
            'success': True,
            'views_count': new_count
        })
        
    except Article.DoesNotExist:
        return JsonResponse({'error': 'Article not found'}, status=404)
    except Exception as e:
        logger.error(f"Error incrementing view count: {str(e)}")
        return JsonResponse({'error': 'Internal server error'}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_article_stats(request, article_id: int):
    """
    Get real-time article statistics (views, likes, comments).
    Public endpoint with caching.
    """
    try:
        stats = {
            'views_count': counter_manager.get_article_views(article_id),
            'likes_count': counter_manager.get_article_like_count(article_id),
            'comments_count': counter_manager.get_article_comment_count(article_id),
        }
        
        return JsonResponse(stats)
        
    except Exception as e:
        logger.error(f"Error getting article stats: {str(e)}")
        return JsonResponse({'error': 'Internal server error'}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@ratelimit(key='user', rate='10/m', method='POST')
def start_editing_session(request, article_id: int):
    """
    Start a collaborative editing session.
    """
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
        
    try:
        from .models import Article
        article = Article.objects.get(id=article_id)
        
        # Check edit permissions
        if not (article.author == request.user or request.user.is_staff):
            return JsonResponse({'error': 'Edit permission required'}, status=403)
        
        session_id = editing_manager.start_editing_session(article, request.user)
        
        return JsonResponse({
            'success': True,
            'session_id': session_id,
            'active_editors': editing_manager.get_active_editors(article_id)
        })
        
    except Article.DoesNotExist:
        return JsonResponse({'error': 'Article not found'}, status=404)
    except Exception as e:
        logger.error(f"Error starting editing session: {str(e)}")
        return JsonResponse({'error': 'Internal server error'}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@login_required
@ratelimit(key='user', rate='60/m', method='POST')
def update_cursor_position(request, article_id: int):
    """
    Update cursor position in collaborative editing.
    High rate limit for smooth collaboration.
    """
    try:
        data = json.loads(request.body)
        cursor_position = data.get('cursor_position', 0)
        
        from .models import Article
        article = Article.objects.get(id=article_id)
        
        # Check edit permissions
        if not (article.author == request.user or request.user.is_staff):
            return JsonResponse({'error': 'Edit permission required'}, status=403)
        
        editing_manager.update_cursor_position(article, request.user, cursor_position)
        
        return JsonResponse({'success': True})
        
    except Article.DoesNotExist:
        return JsonResponse({'error': 'Article not found'}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.error(f"Error updating cursor position: {str(e)}")
        return JsonResponse({'error': 'Internal server error'}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@login_required
@ratelimit(key='user', rate='120/m', method='POST')
def editing_heartbeat(request, article_id: int):
    """
    Send heartbeat to maintain editing session.
    Very high rate limit for active editing sessions.
    """
    try:
        from .models import Article
        article = Article.objects.get(id=article_id)
        
        # Check edit permissions
        if not (article.author == request.user or request.user.is_staff):
            return JsonResponse({'error': 'Edit permission required'}, status=403)
        
        editing_manager.send_heartbeat(article, request.user)
        
        return JsonResponse({'success': True})
        
    except Article.DoesNotExist:
        return JsonResponse({'error': 'Article not found'}, status=404)
    except Exception as e:
        logger.error(f"Error in editing heartbeat: {str(e)}")
        return JsonResponse({'error': 'Internal server error'}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def end_editing_session(request, article_id: int):
    """
    End collaborative editing session.
    """
    try:
        from .models import Article
        article = Article.objects.get(id=article_id)
        
        # Check edit permissions
        if not (article.author == request.user or request.user.is_staff):
            return JsonResponse({'error': 'Edit permission required'}, status=403)
        
        editing_manager.end_editing_session(article, request.user)
        
        return JsonResponse({'success': True})
        
    except Article.DoesNotExist:
        return JsonResponse({'error': 'Article not found'}, status=404)
    except Exception as e:
        logger.error(f"Error ending editing session: {str(e)}")
        return JsonResponse({'error': 'Internal server error'}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_active_editors(request, article_id: int):
    """
    Get list of active editors for an article.
    """
    try:
        active_editors = editing_manager.get_active_editors(article_id)
        return JsonResponse({'active_editors': active_editors})
        
    except Exception as e:
        logger.error(f"Error getting active editors: {str(e)}")
        return JsonResponse({'error': 'Internal server error'}, status=500) 