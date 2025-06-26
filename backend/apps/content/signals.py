"""
Django signals for real-time SSE events and content management.
Automatically publishes events when models are created, updated, or deleted.
"""

from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.utils import timezone
from django.core.cache import cache
from .models import Article, Category
from .events import event_publisher, counter_manager
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Article)
def article_saved_handler(sender, instance, created, **kwargs):
    """
    Handle article creation and updates.
    Publishes real-time events and manages cache invalidation.
    """
    try:
        # Get title safely without triggering additional saves
        try:
            title = instance.title
        except:
            title = f"Article {instance.id}"
            
        if created:
            # New article created
            event_publisher.publish_article_event(instance, "created")
            logger.info(f"Published article created event for: {title}")
        else:
            # Article updated
            action = "updated"
            
            # Check if status changed to published
            if hasattr(instance, '_original_status'):
                if (instance._original_status != 'published' and 
                    instance.status == 'published'):
                    action = "published"
                    if not instance.published_at:
                        instance.published_at = timezone.now()
                        instance.save(update_fields=['published_at'])
            
            event_publisher.publish_article_event(instance, action)
            logger.info(f"Published article {action} event for: {title}")
        
        # Invalidate related counters and caches
        counter_manager.invalidate_article_counters(instance.id)
        
        # Invalidate relevant caches
        cache_keys = [
            f'article_{instance.id}',
            f'author_articles_{instance.author.id}',
            'published_articles_list',
        ]
        
        # Get all available translations for multilingual cache invalidation
        try:
            available_languages = instance.get_available_languages()
            for lang_code in available_languages:
                cache_keys.extend([
                    f'published_articles_list_{lang_code}',
                    f'category_articles_{instance.category.id}_{lang_code}' if instance.category else None,
                ])
        except Exception:
            pass  # Fallback if translation system fails
        
        # Remove None values and delete cache keys
        cache_keys = [key for key in cache_keys if key is not None]
        cache.delete_many(cache_keys)
        
    except Exception as e:
        logger.error(f"Error in article_saved_handler: {str(e)}")


@receiver(pre_save, sender=Article)
def article_pre_save_handler(sender, instance, **kwargs):
    """
    Store original values before save for comparison.
    """
    if instance.pk:
        try:
            original = Article.objects.get(pk=instance.pk)
            instance._original_status = original.status
        except Article.DoesNotExist:
            instance._original_status = None


@receiver(post_delete, sender=Article)
def article_deleted_handler(sender, instance, **kwargs):
    """
    Handle article deletion.
    """
    try:
        event_publisher.publish_article_event(instance, "deleted")
        counter_manager.invalidate_article_counters(instance.id)
        logger.info(f"Published article deleted event for: {instance.title}")
    except Exception as e:
        logger.error(f"Error in article_deleted_handler: {str(e)}")


@receiver(post_save, sender=Category)
def category_saved_handler(sender, instance, created, **kwargs):
    """
    Handle category creation and updates.
    """
    try:
        action = "created" if created else "updated"
        
        # Publish to category channel
        from .channels import ChannelManager
        channel = ChannelManager.get_category_channel(instance.id)
        
        event_data = {
            "type": "category",
            "action": action,
            "data": {
                "id": instance.id,
                "name": instance.safe_translation_getter('name', any_language=True),
                "slug": instance.safe_translation_getter('slug', any_language=True),
                "description": instance.safe_translation_getter('description', any_language=True) or '',
                "created_at": instance.created_at.isoformat(),
                "updated_at": instance.updated_at.isoformat(),
            },
            "metadata": {
                "timestamp": instance.updated_at.isoformat(),
                "channel": channel,
            }
        }
        
        event_publisher.publish_event(channel, event_data)
        try:
            category_name = instance.name
        except:
            category_name = f"Category {instance.id}"
        logger.info(f"Published category {action} event for: {category_name}")
        
    except Exception as e:
        logger.error(f"Error in category_saved_handler: {str(e)}")


# Signal handlers for interactions app
@receiver(post_save, sender='interactions.Comment')
def comment_saved_handler(sender, instance, created, **kwargs):
    """
    Handle comment creation and updates.
    """
    try:
        action = "created" if created else "updated"
        event_publisher.publish_comment_event(instance, action)
        
        # Invalidate comment counter cache
        counter_manager.invalidate_article_counters(instance.article.id)
        
        try:
            article_title = instance.article.title
        except:
            article_title = f"Article {instance.article.id}"
        logger.info(f"Published comment {action} event for article: {article_title}")
        
    except Exception as e:
        logger.error(f"Error in comment_saved_handler: {str(e)}")


@receiver(post_delete, sender='interactions.Comment')
def comment_deleted_handler(sender, instance, **kwargs):
    """
    Handle comment deletion.
    """
    try:
        event_publisher.publish_comment_event(instance, "deleted")
        counter_manager.invalidate_article_counters(instance.article.id)
        try:
            article_title = instance.article.title
        except:
            article_title = f"Article {instance.article.id}"
        logger.info(f"Published comment deleted event for article: {article_title}")
        
    except Exception as e:
        logger.error(f"Error in comment_deleted_handler: {str(e)}")


@receiver(post_save, sender='interactions.Like')
def like_saved_handler(sender, instance, created, **kwargs):
    """
    Handle like creation.
    """
    if created:  # Likes are only created, not updated
        try:
            event_publisher.publish_like_event(instance, "created")
            counter_manager.invalidate_article_counters(instance.article.id)
            try:
                article_title = instance.article.title
            except:
                article_title = f"Article {instance.article.id}"
            logger.info(f"Published like created event for article: {article_title}")
            
        except Exception as e:
            logger.error(f"Error in like_saved_handler: {str(e)}")


@receiver(post_delete, sender='interactions.Like')
def like_deleted_handler(sender, instance, **kwargs):
    """
    Handle like deletion (unlike).
    """
    try:
        event_publisher.publish_like_event(instance, "deleted")
        counter_manager.invalidate_article_counters(instance.article.id)
        try:
            article_title = instance.article.title
        except:
            article_title = f"Article {instance.article.id}"
        logger.info(f"Published like deleted event for article: {article_title}")
        
    except Exception as e:
        logger.error(f"Error in like_deleted_handler: {str(e)}") 