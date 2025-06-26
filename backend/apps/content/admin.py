from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.contrib import messages
from parler.admin import TranslatableAdmin, TranslatableTabularInline
from .models import Article, Category, Tag, ArticleTag


@admin.register(Category)
class CategoryAdmin(TranslatableAdmin):
    """
    Admin interface for Category model with multilingual support.
    """
    list_display = ('name', 'article_count', 'created_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('translations__name', 'translations__description')
    
    def get_prepopulated_fields(self, request, obj=None):
        # Return empty dict for translatable fields as they need special handling
        return {}
    
    def article_count(self, obj):
        """Display the number of articles in this category."""
        count = obj.articles.filter(status='published').count()
        if count:
            url = reverse('admin:content_article_changelist')
            return format_html(
                '<a href="{}?category__id__exact={}">{} articles</a>',
                url, obj.pk, count
            )
        return '0 articles'
    article_count.short_description = 'Articles'


class ArticleTagInline(admin.TabularInline):
    """
    Inline admin for article tags.
    """
    model = ArticleTag
    extra = 1
    autocomplete_fields = ['tag']


@admin.register(Article)
class ArticleAdmin(TranslatableAdmin):
    """
    Enhanced admin interface for Article model with real-time publishing.
    """
    list_display = (
        'title', 'author', 'category', 'status', 'status_badge',
        'get_languages', 'created_at', 'published_at'
    )
    list_filter = (
        'status', 'category', 'created_at', 'published_at', 
        'translations__language_code'
    )
    search_fields = (
        'translations__title', 'translations__content', 
        'author__email', 'author__username'
    )
    autocomplete_fields = ['author', 'category']
    readonly_fields = (
        'created_at', 'updated_at', 'views_count', 
        'reading_time_display', 'featured_image_preview',
        'last_saved_at', 'draft_status'
    )
    actions = ['make_published', 'bulk_publish_with_notification']
    
    inlines = [ArticleTagInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'title', 'slug', 'author', 'category', 'status'
            )
        }),
        ('Content', {
            'fields': (
                'excerpt', 'content', 'draft_status'
            )
        }),
        ('Media', {
            'fields': (
                'featured_image', 'featured_image_preview'
            )
        }),
        ('SEO', {
            'fields': (
                'meta_description', 'meta_keywords'
            ),
            'classes': ('collapse',)
        }),
        ('Statistics', {
            'fields': (
                'reading_time_display', 'views_count', 
                'created_at', 'updated_at', 'published_at', 'last_saved_at'
            ),
            'classes': ('collapse',)
        }),
    )
    
    def get_prepopulated_fields(self, request, obj=None):
        # Return empty dict for translatable fields as they need special handling
        return {}
    
    def status_badge(self, obj):
        """Display status as a colored badge."""
        colors = {
            'draft': '#6b7280',
            'published': '#10b981',
            'archived': '#ef4444'
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px; font-weight: bold;">{}</span>',
            colors.get(obj.status, '#000'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def get_languages(self, obj):
        """Display available languages for the article."""
        return ', '.join(obj.get_available_languages())
    get_languages.short_description = 'Languages'
    
    @admin.action(description='Publish selected articles (triggers real-time updates)')
    def make_published(self, request, queryset):
        """Publish selected articles and trigger real-time notifications."""
        updated = 0
        for article in queryset:
            if article.status != 'published':
                article.status = 'published'
                article.save()  # This triggers the signal
                updated += 1
        
        self.message_user(
            request,
            f'{updated} articles were successfully published with real-time notifications sent.',
            messages.SUCCESS
        )
    
    @admin.action(description='Bulk publish with enhanced notifications')
    def bulk_publish_with_notification(self, request, queryset):
        """Bulk publish articles with enhanced real-time notifications."""
        published_count = 0
        
        for article in queryset.filter(status='draft'):
            article.status = 'published'
            article.save()  # Triggers signal
            published_count += 1
        
        if published_count > 0:
            self.message_user(
                request,
                f'Successfully published {published_count} articles. Real-time notifications sent to all connected clients.',
                messages.SUCCESS
            )
        else:
            self.message_user(
                request,
                'No draft articles selected for publishing.',
                messages.WARNING
            )
    
    def draft_status(self, obj):
        """Display detailed draft status information."""
        if obj.has_draft_changes:
            return format_html(
                '<div style="padding: 10px; background: #fff3cd; border: 1px solid #ffeaa7; border-radius: 4px;">'
                '<strong>Draft Changes Available</strong><br>'
                'Last saved: {}<br>'
                '<small>Changes will be published when status is set to "Published"</small>'
                '</div>',
                obj.last_saved_at.strftime('%Y-%m-%d %H:%M:%S') if obj.last_saved_at else 'Never'
            )
        return format_html(
            '<div style="padding: 10px; background: #d4edda; border: 1px solid #c3e6cb; border-radius: 4px;">'
            '<strong>No Draft Changes</strong><br>'
            'Content is synchronized'
            '</div>'
        )
    draft_status.short_description = 'Draft Information'
    
    def reading_time_display(self, obj):
        """Display reading time in a user-friendly format."""
        if obj.reading_time == 1:
            return f'{obj.reading_time} minute'
        return f'{obj.reading_time} minutes'
    reading_time_display.short_description = 'Reading Time'
    
    def featured_image_preview(self, obj):
        """Display a preview of the featured image."""
        if obj.featured_image:
            return format_html(
                '<img src="{}" style="max-width: 200px; max-height: 200px;" />',
                obj.featured_image.url
            )
        return 'No image'
    featured_image_preview.short_description = 'Image Preview'
    
    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        qs = super().get_queryset(request)
        return qs.select_related('author', 'category')
    
    def save_model(self, request, obj, form, change):
        """Auto-assign author if not set and user is an author."""
        if not obj.author_id and hasattr(request.user, 'is_author') and request.user.is_author:
            obj.author = request.user
        super().save_model(request, obj, form, change)
    
    def get_readonly_fields(self, request, obj=None):
        """Make certain fields readonly for non-superusers."""
        readonly = list(self.readonly_fields)
        if not request.user.is_superuser:
            readonly.extend(['author', 'views_count'])
        return readonly
    
    # Auto-save functionality is handled by Django-Prose-Editor internally
    # No custom URLs needed for basic functionality


@admin.register(Tag)
class TagAdmin(TranslatableAdmin):
    """
    Admin interface for Tag model with multilingual support.
    """
    list_display = ('name', 'article_count', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('translations__name',)
    
    def get_prepopulated_fields(self, request, obj=None):
        # Return empty dict for translatable fields as they need special handling
        return {}
    
    def article_count(self, obj):
        """Display the number of articles with this tag."""
        count = obj.articles.filter(status='published').count()
        if count:
            url = reverse('admin:content_article_changelist')
            return format_html(
                '<a href="{}?tags__id__exact={}">{} articles</a>',
                url, obj.pk, count
            )
        return '0 articles'
    article_count.short_description = 'Articles'


# Customize admin site
admin.site.site_header = 'VITAL MASTERY Administration'
admin.site.site_title = 'VITAL MASTERY Admin'
admin.site.index_title = 'Content Management System' 