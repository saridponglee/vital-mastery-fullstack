from django.contrib import admin
from django.utils.html import format_html
from .models import Comment, Like, Bookmark


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """
    Admin interface for Comment model.
    """
    list_display = (
        'short_content', 'author', 'article_title', 
        'is_approved', 'is_reply', 'created_at'
    )
    list_filter = ('is_approved', 'created_at', 'article__category')
    search_fields = ('content', 'author__username', 'article__translations__title')
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('article', 'author', 'parent')
    
    fieldsets = (
        (None, {
            'fields': ('article', 'author', 'parent')
        }),
        ('Content', {
            'fields': ('content', 'is_approved')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def short_content(self, obj):
        """Display shortened content."""
        return obj.content[:50] + ('...' if len(obj.content) > 50 else '')
    short_content.short_description = 'Content'
    
    def article_title(self, obj):
        """Display article title."""
        title = obj.article.safe_translation_getter('title', any_language=True)
        return title or f'Article {obj.article.pk}'
    article_title.short_description = 'Article'
    
    def is_reply(self, obj):
        """Display if comment is a reply."""
        return obj.is_reply
    is_reply.boolean = True
    is_reply.short_description = 'Reply'
    
    actions = ['approve_comments', 'disapprove_comments']
    
    def approve_comments(self, request, queryset):
        """Approve selected comments."""
        updated = queryset.update(is_approved=True)
        self.message_user(request, f'{updated} comments approved.')
    approve_comments.short_description = 'Approve selected comments'
    
    def disapprove_comments(self, request, queryset):
        """Disapprove selected comments."""
        updated = queryset.update(is_approved=False)
        self.message_user(request, f'{updated} comments disapproved.')
    disapprove_comments.short_description = 'Disapprove selected comments'


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    """
    Admin interface for Like model.
    """
    list_display = ('user', 'article_title', 'created_at')
    list_filter = ('created_at', 'article__category')
    search_fields = ('user__username', 'article__translations__title')
    readonly_fields = ('created_at',)
    raw_id_fields = ('article', 'user')
    
    def article_title(self, obj):
        """Display article title."""
        title = obj.article.safe_translation_getter('title', any_language=True)
        return title or f'Article {obj.article.pk}'
    article_title.short_description = 'Article'


@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    """
    Admin interface for Bookmark model.
    """
    list_display = ('user', 'article_title', 'created_at')
    list_filter = ('created_at', 'article__category')
    search_fields = ('user__username', 'article__translations__title')
    readonly_fields = ('created_at',)
    raw_id_fields = ('article', 'user')
    
    def article_title(self, obj):
        """Display article title."""
        title = obj.article.safe_translation_getter('title', any_language=True)
        return title or f'Article {obj.article.pk}'
    article_title.short_description = 'Article' 