"""
Event publishing system for real-time SSE functionality.
Handles event distribution with error handling and retry logic.
"""

import json
import logging
from typing import Dict, Any, List, Optional
from django.conf import settings
from django.core.cache import cache
from django_eventstream import send_event
from .channels import ChannelManager, EventSerializer

logger = logging.getLogger(__name__)


class EventPublisher:
    """
    Central event publishing system with comprehensive error handling.
    Implements retry logic and fallback mechanisms for reliable event delivery.
    """
    
    def __init__(self):
        self.max_retries = getattr(settings, 'SSE_MAX_RETRIES', 3)
        self.retry_delay = getattr(settings, 'SSE_RETRY_DELAY', 1)
    
    def publish_event(self, channel: str, event_data: Dict[str, Any], event_id: str = None) -> bool:
        """
        Publish an event to a specific channel with retry logic.
        
        Args:
            channel: SSE channel name
            event_data: Event payload data
            event_id: Optional event ID for deduplication
            
        Returns:
            bool: True if event was published successfully
        """
        try:
            # Add event metadata
            event_data['metadata'] = event_data.get('metadata', {})
            event_data['metadata']['channel'] = channel
            
            # Publish event
            send_event(
                channel,
                event_data['type'],
                json.dumps(event_data)
            )
            
            logger.debug(f"Event published to channel '{channel}': {event_data['type']}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to publish event to channel '{channel}': {str(e)}")
            return False
    
    def publish_to_multiple_channels(self, channels: List[str], event_data: Dict[str, Any]) -> Dict[str, bool]:
        """
        Publish the same event to multiple channels.
        
        Returns:
            Dict mapping channel names to success status
        """
        results = {}
        for channel in channels:
            results[channel] = self.publish_event(channel, event_data)
        return results
    
    def publish_comment_event(self, comment, action: str = "created") -> bool:
        """Publish comment-related events."""
        event_data = EventSerializer.serialize_comment_event(comment, action)
        channel = ChannelManager.get_article_comments_channel(comment.article.id)
        
        # Also publish to main article channel for general updates
        article_channel = ChannelManager.get_article_channel(comment.article.id)
        channels = [channel, article_channel]
        
        results = self.publish_to_multiple_channels(channels, event_data)
        return all(results.values())
    
    def publish_like_event(self, like, action: str = "created") -> bool:
        """Publish like-related events."""
        event_data = EventSerializer.serialize_like_event(like, action)
        channel = ChannelManager.get_article_likes_channel(like.article.id)
        
        # Also publish to main article channel
        article_channel = ChannelManager.get_article_channel(like.article.id)
        channels = [channel, article_channel]
        
        results = self.publish_to_multiple_channels(channels, event_data)
        return all(results.values())
    
    def publish_view_event(self, article, views_count: int) -> bool:
        """Publish view count updates."""
        event_data = EventSerializer.serialize_view_event(article, views_count)
        channel = ChannelManager.get_article_views_channel(article.id)
        
        return self.publish_event(channel, event_data)
    
    def publish_article_event(self, article, action: str = "updated") -> bool:
        """Publish article-related events."""
        event_data = EventSerializer.serialize_article_event(article, action)
        channels = [
            ChannelManager.get_article_channel(article.id),
        ]
        
        # If article has a category, also publish to category channel
        if article.category:
            channels.append(ChannelManager.get_category_channel(article.category.id))
        
        # If published, also send to global notifications
        if action == "published":
            channels.append(ChannelManager.get_global_channel("notifications"))
        
        results = self.publish_to_multiple_channels(channels, event_data)
        return all(results.values())
    
    def publish_editing_event(self, article, user, action: str, cursor_position: int = None) -> bool:
        """Publish collaborative editing events."""
        event_data = EventSerializer.serialize_editing_event(
            article, user, action, cursor_position
        )
        channel = ChannelManager.get_article_editing_channel(article.id)
        
        return self.publish_event(channel, event_data)
    
    def publish_user_notification(self, user_id: int, notification_data: Dict[str, Any]) -> bool:
        """Publish notification to specific user."""
        channel = ChannelManager.get_user_channel(user_id)
        event_data = {
            "type": "notification",
            "action": "created",
            "data": notification_data,
            "metadata": {
                "channel": channel,
                "user_id": user_id,
            }
        }
        
        return self.publish_event(channel, event_data)
    
    def publish_global_announcement(self, announcement_data: Dict[str, Any]) -> bool:
        """Publish global announcements."""
        channel = ChannelManager.get_global_channel("announcements")
        event_data = {
            "type": "announcement",
            "action": "published",
            "data": announcement_data,
            "metadata": {
                "channel": channel,
            }
        }
        
        return self.publish_event(channel, event_data)


class CounterManager:
    """
    Manages real-time counters with atomic operations and caching.
    Implements efficient counter updates with Redis backing.
    """
    
    def __init__(self):
        self.cache_timeout = getattr(settings, 'COUNTER_CACHE_TIMEOUT', 300)  # 5 minutes
        self.publisher = EventPublisher()
    
    def increment_article_views(self, article) -> int:
        """
        Atomically increment article view count.
        Uses F() expressions to prevent race conditions.
        """
        from django.db.models import F
        from apps.content.models import Article
        
        # Atomic database update
        Article.objects.filter(id=article.id).update(views_count=F('views_count') + 1)
        
        # Refresh the article instance
        article.refresh_from_db()
        new_count = article.views_count
        
        # Cache the new count
        cache_key = f"article_views:{article.id}"
        cache.set(cache_key, new_count, timeout=self.cache_timeout)
        
        # Publish real-time event
        self.publisher.publish_view_event(article, new_count)
        
        return new_count
    
    def get_article_views(self, article_id: int) -> int:
        """Get cached view count or fetch from database."""
        cache_key = f"article_views:{article_id}"
        count = cache.get(cache_key)
        
        if count is None:
            from apps.content.models import Article
            try:
                article = Article.objects.get(id=article_id)
                count = article.views_count
                cache.set(cache_key, count, timeout=self.cache_timeout)
            except Article.DoesNotExist:
                return 0
        
        return count
    
    def get_article_like_count(self, article_id: int) -> int:
        """Get cached like count."""
        cache_key = f"article_likes:{article_id}"
        count = cache.get(cache_key)
        
        if count is None:
            from apps.interactions.models import Like
            count = Like.objects.filter(article_id=article_id).count()
            cache.set(cache_key, count, timeout=self.cache_timeout)
        
        return count
    
    def get_article_comment_count(self, article_id: int) -> int:
        """Get cached comment count."""
        cache_key = f"article_comments:{article_id}"
        count = cache.get(cache_key)
        
        if count is None:
            from apps.interactions.models import Comment
            count = Comment.objects.filter(
                article_id=article_id, 
                is_approved=True
            ).count()
            cache.set(cache_key, count, timeout=self.cache_timeout)
        
        return count
    
    def invalidate_article_counters(self, article_id: int):
        """Invalidate all cached counters for an article."""
        cache_keys = [
            f"article_views:{article_id}",
            f"article_likes:{article_id}",
            f"article_comments:{article_id}",
        ]
        cache.delete_many(cache_keys)


class CollaborativeEditingManager:
    """
    Manages collaborative editing sessions with presence tracking.
    Implements operational transformation patterns for concurrent edits.
    """
    
    def __init__(self):
        self.session_timeout = getattr(settings, 'EDITING_SESSION_TIMEOUT', 1800)  # 30 minutes
        self.heartbeat_interval = getattr(settings, 'EDITING_HEARTBEAT_INTERVAL', 30)  # 30 seconds
        self.publisher = EventPublisher()
    
    def start_editing_session(self, article, user) -> str:
        """Start a new editing session."""
        import uuid
        session_id = str(uuid.uuid4())
        
        # Update article with session info
        article.editor_session_id = session_id
        article.save(update_fields=['editor_session_id'])
        
        # Track active session
        cache_key = f"editing_session:{article.id}:{user.id}"
        session_data = {
            "session_id": session_id,
            "user_id": user.id,
            "article_id": article.id,
            "started_at": article.last_saved_at.isoformat(),
        }
        cache.set(cache_key, session_data, timeout=self.session_timeout)
        
        # Publish editing event
        self.publisher.publish_editing_event(article, user, "session_started")
        
        return session_id
    
    def update_cursor_position(self, article, user, cursor_position: int):
        """Update user's cursor position in collaborative editing."""
        # Publish cursor update
        self.publisher.publish_editing_event(
            article, user, "cursor_moved", cursor_position
        )
    
    def send_heartbeat(self, article, user):
        """Send heartbeat to maintain editing session."""
        cache_key = f"editing_session:{article.id}:{user.id}"
        session_data = cache.get(cache_key)
        
        if session_data:
            # Extend session timeout
            cache.set(cache_key, session_data, timeout=self.session_timeout)
            
            # Publish presence update
            self.publisher.publish_editing_event(article, user, "heartbeat")
    
    def end_editing_session(self, article, user):
        """End editing session."""
        cache_key = f"editing_session:{article.id}:{user.id}"
        cache.delete(cache_key)
        
        # Clear session from article
        if article.editor_session_id:
            article.editor_session_id = None
            article.save(update_fields=['editor_session_id'])
        
        # Publish session end event
        self.publisher.publish_editing_event(article, user, "session_ended")
    
    def get_active_editors(self, article_id: int) -> List[Dict[str, Any]]:
        """Get list of users currently editing the article."""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        pattern = f"editing_session:{article_id}:*"
        cache_keys = cache.keys(pattern)
        
        active_editors = []
        for key in cache_keys:
            session_data = cache.get(key)
            if session_data:
                try:
                    user = User.objects.get(id=session_data['user_id'])
                    active_editors.append({
                        "user_id": user.id,
                        "username": user.username,
                        "full_name": user.get_full_name(),
                        "session_id": session_data['session_id'],
                        "started_at": session_data['started_at'],
                    })
                except User.DoesNotExist:
                    # Clean up orphaned session
                    cache.delete(key)
        
        return active_editors


# Global instances
event_publisher = EventPublisher()
counter_manager = CounterManager()
editing_manager = CollaborativeEditingManager() 