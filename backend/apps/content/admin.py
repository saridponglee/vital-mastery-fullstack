from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
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
    prepopulated_fields = {'slug': ('name',)}
    
    def get_prepopulated_fields(self, request, obj=None):
        return {'slug': ('name',)}
    
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
    Admin interface for Article model with TinyMCE and multilingual support.
    """
    list_display = (
        'title', 'author', 'category', 'status', 
        'reading_time', 'views_count', 'published_at'
    )
    list_filter = (
        'status', 'category', 'created_at', 'published_at', 
        'author__is_author'
    )
    search_fields = (
        'translations__title', 'translations__content', 
        'author__email', 'author__username'
    )
    autocomplete_fields = ['author', 'category']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = (
        'created_at', 'updated_at', 'views_count', 
        'reading_time_display', 'featured_image_preview'
    )
    
    inlines = [ArticleTagInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'title', 'slug', 'author', 'category', 'status'
            )
        }),
        ('Content', {
            'fields': (
                'excerpt', 'content'
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
                'created_at', 'updated_at', 'published_at'
            ),
            'classes': ('collapse',)
        }),
    )
    
    def get_prepopulated_fields(self, request, obj=None):
        return {'slug': ('title',)}
    
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
        if not obj.author_id and request.user.is_author:
            obj.author = request.user
        super().save_model(request, obj, form, change)
    
    def get_readonly_fields(self, request, obj=None):
        """Make certain fields readonly for non-superusers."""
        readonly = list(self.readonly_fields)
        if not request.user.is_superuser:
            readonly.extend(['author', 'views_count'])
        return readonly
    
    class Media:
        """Include TinyMCE assets."""
        js = (
            '/static/tinymce/tinymce.min.js',
            '/static/admin/js/tinymce_setup.js',
        )


@admin.register(Tag)
class TagAdmin(TranslatableAdmin):
    """
    Admin interface for Tag model with multilingual support.
    """
    list_display = ('name', 'article_count', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('translations__name',)
    prepopulated_fields = {'slug': ('name',)}
    
    def get_prepopulated_fields(self, request, obj=None):
        return {'slug': ('name',)}
    
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