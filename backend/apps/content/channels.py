"""
Channel management system for real-time SSE events.
Implements hierarchical naming conventions and access control patterns.
"""

from typing import List, Dict, Any, Optional
from django.contrib.auth.models import AnonymousUser
from django.conf import settings
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)


class ChannelManager:
    """
    Manages SSE channel organization and access control.
    Implements hierarchical naming conventions for scalable channel management.
    """
    
    # Channel patterns
    USER_CHANNEL = "user-{user_id}"
    ARTICLE_CHANNEL = "article-{article_id}"
    ARTICLE_COMMENTS_CHANNEL = "article-{article_id}-comments"
    ARTICLE_LIKES_CHANNEL = "article-{article_id}-likes"
    ARTICLE_VIEWS_CHANNEL = "article-{article_id}-views"
    ARTICLE_EDITING_CHANNEL = "article-{article_id}-editing"
    CATEGORY_CHANNEL = "category-{category_id}"
    GLOBAL_NOTIFICATIONS = "global-notifications"
    GLOBAL_ANNOUNCEMENTS = "global-announcements"
    
    @classmethod
    def get_user_channel(cls, user_id: int) -> str:
        """Get private channel for specific user."""
        return cls.USER_CHANNEL.format(user_id=user_id)
    
    @classmethod
    def get_article_channel(cls, article_id: int) -> str:
        """Get main channel for article updates."""
        return cls.ARTICLE_CHANNEL.format(article_id=article_id)
    
    @classmethod
    def get_article_comments_channel(cls, article_id: int) -> str:
        """Get channel for article comments."""
        return cls.ARTICLE_COMMENTS_CHANNEL.format(article_id=article_id)
    
    @classmethod
    def get_article_likes_channel(cls, article_id: int) -> str:
        """Get channel for article likes/reactions."""
        return cls.ARTICLE_LIKES_CHANNEL.format(article_id=article_id)
    
    @classmethod
    def get_article_views_channel(cls, article_id: int) -> str:
        """Get channel for article view counts."""
        return cls.ARTICLE_VIEWS_CHANNEL.format(article_id=article_id)
    
    @classmethod
    def get_article_editing_channel(cls, article_id: int) -> str:
        """Get channel for collaborative editing."""
        return cls.ARTICLE_EDITING_CHANNEL.format(article_id=article_id)
    
    @classmethod
    def get_category_channel(cls, category_id: int) -> str:
        """Get channel for category updates."""
        return cls.CATEGORY_CHANNEL.format(category_id=category_id)
    
    @classmethod
    def get_global_channel(cls, channel_type: str = "notifications") -> str:
        """Get global channel for system-wide updates."""
        if channel_type == "announcements":
            return cls.GLOBAL_ANNOUNCEMENTS
        return cls.GLOBAL_NOTIFICATIONS
    
    @classmethod
    def get_user_channels(cls, user_id: int) -> List[str]:
        """Get all channels a user should subscribe to."""
        channels = [
            cls.get_user_channel(user_id),
            cls.get_global_channel("notifications"),
        ]
        return channels
    
    @classmethod
    def get_article_channels(cls, article_id: int) -> List[str]:
        """Get all channels related to an article."""
        return [
            cls.get_article_channel(article_id),
            cls.get_article_comments_channel(article_id),
            cls.get_article_likes_channel(article_id),
            cls.get_article_views_channel(article_id),
            cls.get_article_editing_channel(article_id),
        ]
    
    @classmethod
    def check_channel_permission(cls, user, channel: str) -> bool:
        """
        Check if user has permission to access a channel.
        Implements fine-grained permission control based on channel naming.
        """
        if isinstance(user, AnonymousUser):
            # Anonymous users can only access public channels, but not editing channels
            if "-editing" in channel:
                return False
                
            public_patterns = [
                "article-",
                "category-",
                "global-notifications",
                "global-announcements"
            ]
            return any(channel.startswith(pattern) for pattern in public_patterns)
        
        # Private user channel access
        if channel.startswith("user-"):
            try:
                channel_user_id = int(channel.split("-")[1])
                return channel_user_id == user.id
            except (ValueError, IndexError):
                return False
        
        # Article editing channels require proper permissions
        if "-editing" in channel:
            try:
                article_id = int(channel.split("-")[1])
                from apps.content.models import Article
                try:
                    article = Article.objects.get(id=article_id)
                    return article.author == user or user.is_staff
                except Article.DoesNotExist:
                    return False
            except (ValueError, IndexError):
                return False
        
        # All other channels are publicly accessible for authenticated users
        return True
    
    @classmethod
    def track_connection(cls, user_id: int, channel: str) -> bool:
        """
        Track active connections for rate limiting.
        Returns True if connection is allowed, False if rate limited.
        """
        if not user_id:
            return True  # Skip tracking for anonymous users
        
        cache_key = f"connections:user:{user_id}"
        connections = cache.get(cache_key, set())
        
        max_connections = getattr(settings, 'SSE_MAX_CONNECTIONS_PER_USER', 5)
        if len(connections) >= max_connections:
            logger.warning(f"User {user_id} exceeded max connections ({max_connections})")
            return False
        
        connections.add(channel)
        cache.set(cache_key, connections, timeout=settings.SSE_CONNECTION_TIMEOUT)
        return True
    
    @classmethod
    def release_connection(cls, user_id: int, channel: str):
        """Release a tracked connection."""
        if not user_id:
            return
        
        cache_key = f"connections:user:{user_id}"
        connections = cache.get(cache_key, set())
        connections.discard(channel)
        
        if connections:
            cache.set(cache_key, connections, timeout=settings.SSE_CONNECTION_TIMEOUT)
        else:
            cache.delete(cache_key)


class EventSerializer:
    """
    Standardizes event payload structure for consistent SSE communication.
    """
    
    @staticmethod
    def serialize_comment_event(comment, action: str = "created") -> Dict[str, Any]:
        """Serialize comment events."""
        return {
            "type": "comment",
            "action": action,
            "data": {
                "id": comment.id,
                "article_id": comment.article.id,
                "author": {
                    "id": comment.author.id,
                    "username": comment.author.username,
                    "full_name": comment.author.get_full_name(),
                },
                "content": comment.content,
                "parent_id": comment.parent.id if comment.parent else None,
                "created_at": comment.created_at.isoformat(),
                "updated_at": comment.updated_at.isoformat(),
                "is_reply": comment.is_reply,
            },
            "metadata": {
                "timestamp": comment.updated_at.isoformat(),
                "channel": ChannelManager.get_article_comments_channel(comment.article.id),
            }
        }
    
    @staticmethod
    def serialize_like_event(like, action: str = "created") -> Dict[str, Any]:
        """Serialize like events."""
        return {
            "type": "like",
            "action": action,
            "data": {
                "id": like.id,
                "article_id": like.article.id,
                "user_id": like.user.id,
                "created_at": like.created_at.isoformat(),
            },
            "metadata": {
                "timestamp": like.created_at.isoformat(),
                "channel": ChannelManager.get_article_likes_channel(like.article.id),
            }
        }
    
    @staticmethod
    def serialize_view_event(article, views_count: int) -> Dict[str, Any]:
        """Serialize view count events."""
        return {
            "type": "view",
            "action": "incremented",
            "data": {
                "article_id": article.id,
                "views_count": views_count,
            },
            "metadata": {
                "timestamp": article.updated_at.isoformat(),
                "channel": ChannelManager.get_article_views_channel(article.id),
            }
        }
    
    @staticmethod
    def serialize_article_event(article, action: str = "updated") -> Dict[str, Any]:
        """Serialize article events."""
        try:
            title = article.title
            slug = article.slug
        except:
            # If translation doesn't exist, use fallback values
            title = f"Article {article.id}"
            slug = f"article-{article.id}"
            
        return {
            "type": "article",
            "action": action,
            "data": {
                "id": article.id,
                "title": title,
                "slug": slug,
                "status": article.status,
                "author": {
                    "id": article.author.id,
                    "username": article.author.username,
                },
                "category_id": article.category.id if article.category else None,
                "reading_time": article.reading_time,
                "views_count": article.views_count,
                "created_at": article.created_at.isoformat(),
                "updated_at": article.updated_at.isoformat(),
                "published_at": article.published_at.isoformat() if article.published_at else None,
            },
            "metadata": {
                "timestamp": article.updated_at.isoformat(),
                "channel": ChannelManager.get_article_channel(article.id),
            }
        }
    
    @staticmethod
    def serialize_editing_event(article, user, action: str, cursor_position: int = None) -> Dict[str, Any]:
        """Serialize collaborative editing events."""
        return {
            "type": "editing",
            "action": action,
            "data": {
                "article_id": article.id,
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "full_name": user.get_full_name(),
                },
                "cursor_position": cursor_position,
                "session_id": article.editor_session_id,
                "is_auto_saving": article.is_auto_saving,
            },
            "metadata": {
                "timestamp": article.last_saved_at.isoformat(),
                "channel": ChannelManager.get_article_editing_channel(article.id),
            }
        } 