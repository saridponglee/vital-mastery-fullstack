"""
Comprehensive test suite for real-time SSE functionality.

Tests cover:
- Channel management and access control
- Event serialization and publishing  
- Counter management with caching
- Collaborative editing functionality
- Django signals integration
- SSE view endpoints
"""

import json
import time
from unittest.mock import Mock, patch, MagicMock
from django.test import TestCase, TransactionTestCase, override_settings
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.cache import cache
from django.test.client import Client
from django.utils import timezone, translation
from apps.content.models import Article, Category
from apps.interactions.models import Comment, Like, Bookmark
from apps.content.channels import ChannelManager
from apps.content.events import EventPublisher, EventSerializer, counter_manager, editing_manager
from apps.content.signals import *

User = get_user_model()


class MockEventSource:
    """Mock EventSource for testing SSE functionality."""
    
    def __init__(self):
        self.events = []
        self.listeners = {}
        self.state = 'connecting'
    
    def addEventListener(self, event_type, handler):
        if event_type not in self.listeners:
            self.listeners[event_type] = []
        self.listeners[event_type].append(handler)
    
    def send_mock_event(self, event_type, data):
        """Simulate receiving an SSE event."""
        mock_event = Mock()
        mock_event.data = json.dumps(data) if isinstance(data, dict) else data
        mock_event.type = event_type
        
        if event_type in self.listeners:
            for handler in self.listeners[event_type]:
                handler(mock_event)
    
    def close(self):
        self.state = 'closed'


@override_settings(
    LANGUAGE_CODE='en',
    PARLER_LANGUAGES={
        None: (
            {'code': 'en'},
            {'code': 'th'},
        ),
        'default': {
            'fallbacks': ['en'],
            'hide_untranslated': False,
        }
    }
)
class ChannelManagerTestCase(TestCase):
    """Test channel management and access control."""
    
    def setUp(self):
        # Activate English language for tests
        translation.activate('en')
        
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.staff_user = User.objects.create_user(
            username='staffuser',
            email='staff@example.com',
            password='staffpass123',
            is_staff=True
        )
        # Create category with proper language setup
        with translation.override('en'):
            self.category = Category.objects.create()
            self.category.translations.create(
                language_code='en',
                name='Test Category',
                slug='test-category'
            )
        self.article = Article.objects.create(
            author=self.user,
            category=self.category,
            status='published'
        )
        self.article.translations.create(
            language_code='en',
            title='Test Article',
            slug='test-article',
            content='Test content'
        )
    
    def test_channel_naming_conventions(self):
        """Test hierarchical channel naming patterns."""
        # User channels
        user_channel = ChannelManager.get_user_channel(self.user.id)
        self.assertEqual(user_channel, f"user-{self.user.id}")
        
        # Article channels
        article_channel = ChannelManager.get_article_channel(self.article.id)
        self.assertEqual(article_channel, f"article-{self.article.id}")
        
        comments_channel = ChannelManager.get_article_comments_channel(self.article.id)
        self.assertEqual(comments_channel, f"article-{self.article.id}-comments")
        
        likes_channel = ChannelManager.get_article_likes_channel(self.article.id)
        self.assertEqual(likes_channel, f"article-{self.article.id}-likes")
        
        editing_channel = ChannelManager.get_article_editing_channel(self.article.id)
        self.assertEqual(editing_channel, f"article-{self.article.id}-editing")
        
        # Global channels
        notifications_channel = ChannelManager.get_global_channel("notifications")
        self.assertEqual(notifications_channel, "global-notifications")
        
        announcements_channel = ChannelManager.get_global_channel("announcements")
        self.assertEqual(announcements_channel, "global-announcements")
    
    def test_channel_permissions_authenticated_user(self):
        """Test channel access permissions for authenticated users."""
        # User should access their own channel
        own_channel = ChannelManager.get_user_channel(self.user.id)
        self.assertTrue(ChannelManager.check_channel_permission(self.user, own_channel))
        
        # User should not access other user's channel
        other_channel = ChannelManager.get_user_channel(self.staff_user.id)
        self.assertFalse(ChannelManager.check_channel_permission(self.user, other_channel))
        
        # User should access public article channels
        article_channel = ChannelManager.get_article_channel(self.article.id)
        self.assertTrue(ChannelManager.check_channel_permission(self.user, article_channel))
        
        # User should access editing channel for their own article
        editing_channel = ChannelManager.get_article_editing_channel(self.article.id)
        self.assertTrue(ChannelManager.check_channel_permission(self.user, editing_channel))
        
        # User should not access editing channel for other's article
        other_article = Article.objects.create(
            author=self.staff_user,
            category=self.category,
            status='published'
        )
        other_editing_channel = ChannelManager.get_article_editing_channel(other_article.id)
        self.assertFalse(ChannelManager.check_channel_permission(self.user, other_editing_channel))
        
        # Staff user should access any editing channel
        self.assertTrue(ChannelManager.check_channel_permission(self.staff_user, other_editing_channel))
    
    def test_channel_permissions_anonymous_user(self):
        """Test channel access permissions for anonymous users."""
        from django.contrib.auth.models import AnonymousUser
        anon_user = AnonymousUser()
        
        # Anonymous users can access public channels
        article_channel = ChannelManager.get_article_channel(self.article.id)
        self.assertTrue(ChannelManager.check_channel_permission(anon_user, article_channel))
        
        global_channel = ChannelManager.get_global_channel("notifications")
        self.assertTrue(ChannelManager.check_channel_permission(anon_user, global_channel))
        
        # Anonymous users cannot access private channels
        user_channel = ChannelManager.get_user_channel(self.user.id)
        self.assertFalse(ChannelManager.check_channel_permission(anon_user, user_channel))
        
        editing_channel = ChannelManager.get_article_editing_channel(self.article.id)
        self.assertFalse(ChannelManager.check_channel_permission(anon_user, editing_channel))
    
    @override_settings(SSE_MAX_CONNECTIONS_PER_USER=2)
    def test_connection_rate_limiting(self):
        """Test connection rate limiting functionality."""
        channel1 = "test-channel-1"
        channel2 = "test-channel-2"
        channel3 = "test-channel-3"
        
        # Should allow first two connections
        self.assertTrue(ChannelManager.track_connection(self.user.id, channel1))
        self.assertTrue(ChannelManager.track_connection(self.user.id, channel2))
        
        # Should reject third connection (exceeds limit)
        self.assertFalse(ChannelManager.track_connection(self.user.id, channel3))
        
        # Release one connection and try again
        ChannelManager.release_connection(self.user.id, channel1)
        self.assertTrue(ChannelManager.track_connection(self.user.id, channel3))


@override_settings(
    LANGUAGE_CODE='en',
    PARLER_LANGUAGES={
        None: (
            {'code': 'en'},
            {'code': 'th'},
        ),
        'default': {
            'fallbacks': ['en'],
            'hide_untranslated': False,
        }
    }
)
class EventSerializerTestCase(TestCase):
    """Test event serialization for consistent SSE payloads."""
    
    def setUp(self):
        # Activate English language for tests
        translation.activate('en')
        
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        # Create category and article with proper language setup
        with translation.override('en'):
            self.category = Category.objects.create()
            self.category.translations.create(
                language_code='en',
                name='Test Category',
                slug='test-category'
            )
            self.article = Article.objects.create(
                author=self.user,
                category=self.category,
                status='published'
            )
            self.article.translations.create(
                language_code='en',
                title='Test Article',
                slug='test-article',
                content='Test content'
            )
    
    def test_comment_event_serialization(self):
        """Test comment event serialization structure."""
        comment = Comment.objects.create(
            article=self.article,
            author=self.user,
            content='Test comment'
        )
        
        event_data = EventSerializer.serialize_comment_event(comment, "created")
        
        # Check event structure
        self.assertEqual(event_data['type'], 'comment')
        self.assertEqual(event_data['action'], 'created')
        self.assertIn('data', event_data)
        self.assertIn('metadata', event_data)
        
        # Check data content
        data = event_data['data']
        self.assertEqual(data['id'], comment.id)
        self.assertEqual(data['article_id'], self.article.id)
        self.assertEqual(data['author']['id'], self.user.id)
        self.assertEqual(data['content'], 'Test comment')
        self.assertIsNone(data['parent_id'])
        self.assertFalse(data['is_reply'])
        
        # Check metadata
        metadata = event_data['metadata']
        self.assertIn('timestamp', metadata)
        self.assertIn('channel', metadata)
    
    def test_like_event_serialization(self):
        """Test like event serialization structure."""
        like = Like.objects.create(
            article=self.article,
            user=self.user
        )
        
        event_data = EventSerializer.serialize_like_event(like, "created")
        
        self.assertEqual(event_data['type'], 'like')
        self.assertEqual(event_data['action'], 'created')
        self.assertEqual(event_data['data']['article_id'], self.article.id)
        self.assertEqual(event_data['data']['user_id'], self.user.id)
    
    def test_view_event_serialization(self):
        """Test view count event serialization."""
        event_data = EventSerializer.serialize_view_event(self.article, 42)
        
        self.assertEqual(event_data['type'], 'view')
        self.assertEqual(event_data['action'], 'incremented')
        self.assertEqual(event_data['data']['article_id'], self.article.id)
        self.assertEqual(event_data['data']['views_count'], 42)
    
    def test_article_event_serialization(self):
        """Test article event serialization."""
        event_data = EventSerializer.serialize_article_event(self.article, "updated")
        
        self.assertEqual(event_data['type'], 'article')
        self.assertEqual(event_data['action'], 'updated')
        self.assertEqual(event_data['data']['id'], self.article.id)
        self.assertEqual(event_data['data']['author']['id'], self.user.id)


@override_settings(
    LANGUAGE_CODE='en',
    PARLER_LANGUAGES={
        None: (
            {'code': 'en'},
            {'code': 'th'},
        ),
        'default': {
            'fallbacks': ['en'],
            'hide_untranslated': False,
        }
    }
)
class EventPublisherTestCase(TestCase):
    """Test event publishing functionality."""
    
    def setUp(self):
        # Activate English language for tests
        translation.activate('en')
        
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.category = Category.objects.create()
        self.category.translations.create(
            language_code='en',
            name='Test Category',
            slug='test-category'
        )
        self.article = Article.objects.create(
            author=self.user,
            category=self.category,
            status='published'
        )
        self.article.translations.create(
            language_code='en',
            title='Test Article',
            slug='test-article',
            content='Test content'
        )
        self.publisher = EventPublisher()
    
    @patch('apps.content.events.send_event')
    def test_event_publishing(self, mock_send_event):
        """Test basic event publishing functionality."""
        mock_send_event.return_value = True
        
        event_data = {
            'type': 'test',
            'action': 'created',
            'data': {'test': 'data'}
        }
        
        result = self.publisher.publish_event('test-channel', event_data)
        
        self.assertTrue(result)
        mock_send_event.assert_called_once()
        
        # Check call arguments
        call_args = mock_send_event.call_args
        self.assertEqual(call_args[0][0], 'test-channel')  # channel
        self.assertEqual(call_args[0][1], 'test')  # event type
    
    @patch('apps.content.events.send_event')
    def test_comment_event_publishing(self, mock_send_event):
        """Test comment event publishing."""
        mock_send_event.return_value = True
        
        comment = Comment.objects.create(
            article=self.article,
            author=self.user,
            content='Test comment'
        )
        
        result = self.publisher.publish_comment_event(comment, "created")
        
        self.assertTrue(result)
        # Should be called four times: comment channel + article channel for both comment-specific and main article events
        self.assertEqual(mock_send_event.call_count, 4)
    
    @patch('apps.content.events.send_event')
    def test_like_event_publishing(self, mock_send_event):
        """Test like event publishing."""
        mock_send_event.return_value = True
        
        like = Like.objects.create(
            article=self.article,
            user=self.user
        )
        
        result = self.publisher.publish_like_event(like, "created")
        
        self.assertTrue(result)
        # Should be called four times: like channel + article channel for both like-specific and main article events
        self.assertEqual(mock_send_event.call_count, 4)


@override_settings(
    LANGUAGE_CODE='en',
    PARLER_LANGUAGES={
        None: (
            {'code': 'en'},
            {'code': 'th'},
        ),
        'default': {
            'fallbacks': ['en'],
            'hide_untranslated': False,
        }
    }
)
class CounterManagerTestCase(TestCase):
    """Test real-time counter management."""
    
    def setUp(self):
        # Activate English language for tests
        translation.activate('en')
        
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.category = Category.objects.create()
        self.category.translations.create(
            language_code='en',
            name='Test Category',
            slug='test-category'
        )
        self.article = Article.objects.create(
            author=self.user,
            category=self.category,
            status='published',
            views_count=10
        )
        self.article.translations.create(
            language_code='en',
            title='Test Article',
            slug='test-article',
            content='Test content'
        )
        # Use the global counter_manager instance
    
    def tearDown(self):
        # Clear cache after each test
        cache.clear()
    
    @patch('apps.content.events.EventPublisher.publish_view_event')
    def test_atomic_view_increment(self, mock_publish):
        """Test atomic view count increment."""
        mock_publish.return_value = True
        
        initial_count = self.article.views_count
        new_count = counter_manager.increment_article_views(self.article)
        
        # Refresh article from database
        self.article.refresh_from_db()
        
        self.assertEqual(new_count, initial_count + 1)
        self.assertEqual(self.article.views_count, initial_count + 1)
        mock_publish.assert_called_once()
    
    def test_cached_counter_retrieval(self):
        """Test counter caching functionality."""
        # First call should hit the database
        count1 = counter_manager.get_article_views(self.article.id)
        
        # Second call should use cache
        count2 = counter_manager.get_article_views(self.article.id)
        
        self.assertEqual(count1, count2)
        self.assertEqual(count1, self.article.views_count)
    
    def test_counter_cache_invalidation(self):
        """Test cache invalidation for counters."""
        # Prime the cache
        counter_manager.get_article_views(self.article.id)
        counter_manager.get_article_like_count(self.article.id)
        counter_manager.get_article_comment_count(self.article.id)
        
        # Invalidate counters
        counter_manager.invalidate_article_counters(self.article.id)
        
        # Cache should be cleared
        cache_key = f"article_views:{self.article.id}"
        self.assertIsNone(cache.get(cache_key))


@override_settings(
    LANGUAGE_CODE='en',
    PARLER_LANGUAGES={
        None: (
            {'code': 'en'},
            {'code': 'th'},
        ),
        'default': {
            'fallbacks': ['en'],
            'hide_untranslated': False,
        }
    }
)
class CollaborativeEditingTestCase(TestCase):
    """Test collaborative editing functionality."""
    
    def setUp(self):
        # Activate English language for tests
        translation.activate('en')
        
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='pass123'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='pass123'
        )
        self.category = Category.objects.create()
        self.category.translations.create(
            language_code='en',
            name='Test Category',
            slug='test-category'
        )
        self.article = Article.objects.create(
            author=self.user1,
            category=self.category,
            status='draft'
        )
        self.article.translations.create(
            language_code='en',
            title='Test Article',
            slug='test-article',
            content='Test content'
        )
        # Use the global editing_manager instance
    
    def tearDown(self):
        cache.clear()
    
    @patch('apps.content.events.EventPublisher.publish_editing_event')
    def test_editing_session_start(self, mock_publish):
        """Test starting editing session."""
        mock_publish.return_value = True
        
        session_id = editing_manager.start_editing_session(self.article, self.user1)
        
        self.assertIsNotNone(session_id)
        self.article.refresh_from_db()
        self.assertEqual(self.article.editor_session_id, session_id)
        mock_publish.assert_called_once()
    
    @patch('apps.content.events.EventPublisher.publish_editing_event')
    def test_multiple_editing_sessions(self, mock_publish):
        """Test multiple concurrent editing sessions."""
        mock_publish.return_value = True
        
        # Start sessions for both users
        session1 = editing_manager.start_editing_session(self.article, self.user1)
        session2 = editing_manager.start_editing_session(self.article, self.user2)
        
        # Get active editors
        active_editors = editing_manager.get_active_editors(self.article.id)
        
        self.assertEqual(len(active_editors), 2)
        user_ids = [editor['user_id'] for editor in active_editors]
        self.assertIn(self.user1.id, user_ids)
        self.assertIn(self.user2.id, user_ids)
    
    @patch('apps.content.events.EventPublisher.publish_editing_event')
    def test_editing_session_cleanup(self, mock_publish):
        """Test editing session cleanup."""
        mock_publish.return_value = True
        
        # Start session
        session_id = editing_manager.start_editing_session(self.article, self.user1)
        
        # End session
        editing_manager.end_editing_session(self.article, self.user1)
        
        # Check cleanup
        self.article.refresh_from_db()
        self.assertIsNone(self.article.editor_session_id)
        
        active_editors = editing_manager.get_active_editors(self.article.id)
        self.assertEqual(len(active_editors), 0)


@override_settings(
    LANGUAGE_CODE='en',
    PARLER_LANGUAGES={
        None: (
            {'code': 'en'},
            {'code': 'th'},
        ),
        'default': {
            'fallbacks': ['en'],
            'hide_untranslated': False,
        }
    }
)
class SignalTestCase(TransactionTestCase):
    """Test Django signals for real-time events."""
    
    def setUp(self):
        # Activate English language for tests
        translation.activate('en')
        
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.category = Category.objects.create()
        self.category.translations.create(
            language_code='en',
            name='Test Category',
            slug='test-category'
        )
    
    @patch('apps.content.events.event_publisher.publish_article_event')
    def test_article_creation_signal(self, mock_publish):
        """Test article creation triggers signal."""
        mock_publish.return_value = True
        
        article = Article.objects.create(
            author=self.user,
            category=self.category,
            status='draft'
        )
        article.translations.create(
            language_code='en',
            title='Test Article',
            slug='test-article',
            content='Test content'
        )
        
        mock_publish.assert_called_with(article, "created")
    
    @patch('apps.content.events.event_publisher.publish_comment_event')
    def test_comment_creation_signal(self, mock_publish):
        """Test comment creation triggers signal."""
        mock_publish.return_value = True
        
        article = Article.objects.create(
            author=self.user,
            category=self.category,
            status='published'
        )
        article.translations.create(
            language_code='en',
            title='Test Article',
            slug='test-article',
            content='Test content'
        )
        
        comment = Comment.objects.create(
            article=article,
            author=self.user,
            content='Test comment'
        )
        
        mock_publish.assert_called_with(comment, "created")
    
    @patch('apps.content.events.event_publisher.publish_like_event')
    def test_like_creation_signal(self, mock_publish):
        """Test like creation triggers signal."""
        mock_publish.return_value = True
        
        article = Article.objects.create(
            author=self.user,
            category=self.category,
            status='published'
        )
        
        like = Like.objects.create(
            article=article,
            user=self.user
        )
        
        mock_publish.assert_called_with(like, "created")


@override_settings(
    LANGUAGE_CODE='en',
    PARLER_LANGUAGES={
        None: (
            {'code': 'en'},
            {'code': 'th'},
        ),
        'default': {
            'fallbacks': ['en'],
            'hide_untranslated': False,
        }
    }
)
class SSEViewTestCase(TestCase):
    """Test SSE view endpoints."""
    
    def setUp(self):
        # Activate English language for tests
        translation.activate('en')
        
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.category = Category.objects.create()
        self.category.translations.create(
            language_code='en',
            name='Test Category',
            slug='test-category'
        )
        self.article = Article.objects.create(
            author=self.user,
            category=self.category,
            status='published'
        )
        self.article.translations.create(
            language_code='en',
            title='Test Article',
            slug='test-article',
            content='Test content'
        )
    
    def test_article_stats_endpoint(self):
        """Test article statistics endpoint."""
        url = reverse('content:article-stats', kwargs={'article_id': self.article.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertIn('views_count', data)
        self.assertIn('likes_count', data)
        self.assertIn('comments_count', data)
    
    def test_increment_views_authenticated(self):
        """Test view increment endpoint with authentication."""
        self.client.force_login(self.user)
        
        initial_views = self.article.views_count
        url = reverse('content:increment-views', kwargs={'article_id': self.article.id})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertTrue(data['success'])
        self.assertEqual(data['views_count'], initial_views + 1)
    
    def test_increment_views_unauthenticated(self):
        """Test view increment requires authentication."""
        url = reverse('content:increment-views', kwargs={'article_id': self.article.id})
        response = self.client.post(url)
        
        # Should return 401 for unauthenticated user
        self.assertEqual(response.status_code, 401)
    
    @patch('apps.content.events.editing_manager.start_editing_session')
    def test_start_editing_session(self, mock_start):
        """Test starting editing session endpoint."""
        mock_start.return_value = 'test-session-id'
        
        self.client.force_login(self.user)
        url = reverse('content:start-editing', kwargs={'article_id': self.article.id})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertTrue(data['success'])
        self.assertEqual(data['session_id'], 'test-session-id')
    
    def test_start_editing_session_permission_denied(self):
        """Test editing session requires proper permissions."""
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='pass123'
        )
        self.client.force_login(other_user)
        
        url = reverse('content:start-editing', kwargs={'article_id': self.article.id})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, 403)


# Utility functions for testing
def create_mock_sse_event(event_type: str, action: str, data: dict) -> dict:
    """Create a mock SSE event for testing."""
    return {
        'type': event_type,
        'action': action,
        'data': data,
        'metadata': {
            'timestamp': '2024-01-01T00:00:00Z',
            'channel': f'test-{event_type}-channel',
        }
    }


def assert_sse_event_structure(test_case, event_data: dict):
    """Assert that an SSE event has the correct structure."""
    test_case.assertIn('type', event_data)
    test_case.assertIn('action', event_data)
    test_case.assertIn('data', event_data)
    test_case.assertIn('metadata', event_data)
    test_case.assertIn('timestamp', event_data['metadata'])
    test_case.assertIn('channel', event_data['metadata']) 