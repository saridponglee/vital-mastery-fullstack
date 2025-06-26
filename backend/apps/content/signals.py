from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from django.db import transaction
from django_eventstream import send_event
from django.core.cache import cache
from .models import Article


@receiver(pre_save, sender=Article)
def track_status_changes(sender, instance, **kwargs):
    """Track status changes before saving"""
    if instance.pk:
        try:
            old_instance = Article.objects.get(pk=instance.pk)
            instance._old_status = old_instance.status
        except Article.DoesNotExist:
            instance._old_status = None
    else:
        instance._old_status = None


@receiver(post_save, sender=Article, dispatch_uid="article_status_handler")
def handle_article_status_change(sender, instance, created, **kwargs):
    """Handle automatic actions based on status changes"""
    old_status = getattr(instance, '_old_status', None)
    current_status = instance.status
    
    # Only process if status changed to published
    if current_status == 'published' and old_status != 'published':
        # Set published timestamp
        if not instance.published_at:
            instance.published_at = timezone.now()
            instance.save(update_fields=['published_at'])
        
        # Get all available translations
        available_languages = instance.get_available_languages()
        
        # Send real-time notification for each language
        for lang_code in available_languages:
            instance.set_current_language(lang_code)
            
            # Prepare article data for SSE
            article_data = {
                'id': instance.id,
                'title': instance.title,
                'slug': instance.slug,
                'excerpt': instance.excerpt or '',
                'content': instance.content or '',
                'author': {
                    'id': instance.author.id,
                    'username': instance.author.username,
                    'first_name': getattr(instance.author, 'first_name', ''),
                    'last_name': getattr(instance.author, 'last_name', ''),
                },
                'category': {
                    'id': instance.category.id if instance.category else None,
                    'name': instance.category.safe_translation_getter('name', language_code=lang_code) if instance.category else None,
                } if instance.category else None,
                'featured_image': instance.featured_image.url if instance.featured_image else None,
                'reading_time': instance.reading_time,
                'published_at': instance.published_at.isoformat(),
                'language': lang_code,
                'meta_description': instance.meta_description or '',
            }
            
            # Send SSE event
            send_event(f'article-updates-{lang_code}', 'article-published', article_data)
        
        # Invalidate relevant caches
        cache_keys = [
            f'article_{instance.id}',
            f'author_articles_{instance.author.id}',
            'published_articles_list',
        ]
        for lang_code in available_languages:
            cache_keys.extend([
                f'published_articles_list_{lang_code}',
                f'category_articles_{instance.category.id}_{lang_code}' if instance.category else None,
            ])
        
        # Remove None values and delete cache keys
        cache_keys = [key for key in cache_keys if key is not None]
        cache.delete_many(cache_keys)
        
        print(f"Real-time notification sent for article: {instance.title} (ID: {instance.id})") 