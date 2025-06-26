from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils.text import slugify
from parler.models import TranslatableModel, TranslatedFields
from django_prose_editor.fields import ProseEditorField
import re


class Category(TranslatableModel):
    """
    Category model for organizing articles with multilingual support.
    """
    
    translations = TranslatedFields(
        name=models.CharField(
            max_length=100,
            help_text='Category name'
        ),
        slug=models.SlugField(
            max_length=100,
            unique=True,
            help_text='URL-friendly slug for category'
        ),
        description=models.TextField(
            max_length=500,
            blank=True,
            help_text='Category description'
        )
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['translations__name']
    
    def __str__(self):
        return self.safe_translation_getter('name', any_language=True) or f'Category {self.pk}'
    
    def save(self, *args, **kwargs):
        # Only auto-generate slug if we have a translation with name
        if hasattr(self, 'name') and self.name and (not hasattr(self, 'slug') or not self.slug):
            try:
                self.slug = slugify(self.name)
            except:
                # If translation doesn't exist yet, skip slug generation
                pass
        super().save(*args, **kwargs)


class Article(TranslatableModel):
    """
    Article model with multilingual content support and enhanced draft management.
    """
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]
    
    # Non-translatable fields
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='articles',
        help_text='Article author'
    )
    
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='articles',
        help_text='Article category'
    )
    
    featured_image = models.ImageField(
        upload_to='articles/images/',
        null=True,
        blank=True,
        help_text='Featured image for the article'
    )
    
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='draft',
        help_text='Publication status'
    )
    
    reading_time = models.PositiveIntegerField(
        default=1,
        help_text='Estimated reading time in minutes'
    )
    
    views_count = models.PositiveIntegerField(
        default=0,
        help_text='Number of views'
    )
    
    # Enhanced draft management fields
    last_saved_at = models.DateTimeField(
        auto_now=True,
        help_text='Last auto-save timestamp'
    )
    
    editor_session_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text='Current editor session identifier'
    )
    
    is_auto_saving = models.BooleanField(
        default=False,
        help_text='Indicates if auto-save is in progress'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True, help_text='Timestamp when article was published')
    
    # Translatable fields with enhanced draft support
    translations = TranslatedFields(
        title=models.CharField(
            max_length=255,
            help_text='Article title'
        ),
        slug=models.SlugField(
            max_length=255,
            unique=True,
            help_text='URL-friendly slug for article'
        ),
        excerpt=models.TextField(
            max_length=300,
            blank=True,
            help_text='Short excerpt or summary'
        ),
        content=ProseEditorField(
            extensions={
                "Bold": True,
                "Italic": True,
                "Strike": True,
                "Underline": True,
                "Code": True,
                "Heading": {"levels": [1, 2, 3, 4, 5, 6]},
                "BulletList": True,
                "OrderedList": True,
                "Blockquote": True,
                "HorizontalRule": True,
                "Link": {
                    "enableTarget": True,
                    "protocols": ["http", "https", "mailto"]
                },
                "Table": True,
                "History": True,
                "HTML": True,
                "Typographic": True,
            },
            sanitize=True,
            help_text='Published article content (HTML)'
        ),
        draft_content=ProseEditorField(
            extensions={
                "Bold": True,
                "Italic": True,
                "Strike": True,
                "Underline": True,
                "Code": True,
                "Heading": {"levels": [1, 2, 3, 4, 5, 6]},
                "BulletList": True,
                "OrderedList": True,
                "Blockquote": True,
                "HorizontalRule": True,
                "Link": {
                    "enableTarget": True,
                    "protocols": ["http", "https", "mailto"]
                },
                "Table": True,
                "History": True,
                "HTML": True,
                "Typographic": True,
            },
            sanitize=True,
            blank=True,
            null=True,
            help_text='Draft content that may differ from published content'
        ),
        meta_description=models.TextField(
            max_length=160,
            blank=True,
            help_text='SEO meta description'
        ),
        meta_keywords=models.CharField(
            max_length=255,
            blank=True,
            help_text='SEO meta keywords'
        )
    )
    
    class Meta:
        verbose_name = 'Article'
        verbose_name_plural = 'Articles'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['status', '-published_at']),
            models.Index(fields=['author', 'status']),
        ]
    
    def __str__(self):
        title = self.safe_translation_getter('title', any_language=True)
        return title or f'Article {self.pk}'
    
    def save(self, *args, **kwargs):
        # Auto-generate slug from title if not provided
        try:
            if hasattr(self, 'title') and self.title and (not hasattr(self, 'slug') or not self.slug):
                self.slug = slugify(self.title)
        except:
            # If translation doesn't exist yet, skip slug generation
            pass
        
        # Calculate reading time based on content
        try:
            content_for_calculation = None
            if hasattr(self, 'draft_content'):
                content_for_calculation = self.draft_content
            if not content_for_calculation and hasattr(self, 'content'):
                content_for_calculation = self.content
                
            if content_for_calculation:
                word_count = self.get_word_count(content_for_calculation)
                self.reading_time = max(1, word_count // 250)  # Assume 250 words per minute
        except:
            # If translation doesn't exist yet, skip reading time calculation
            pass
        
        # Set published_at when status changes to published
        if self.status == 'published' and not self.published_at:
            from django.utils import timezone
            self.published_at = timezone.now()
            
            # When publishing, move draft content to main content if exists
            try:
                if hasattr(self, 'draft_content') and self.draft_content:
                    self.content = self.draft_content
            except:
                # If translation doesn't exist yet, skip content migration
                pass
        
        super().save(*args, **kwargs)
    
    def get_word_count(self, content=None):
        """Calculate word count from content (removing HTML tags)."""
        if content is None:
            content = getattr(self, 'content', '')
        
        if not content:
            return 0
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', content)
        # Count words (handle Thai text which doesn't use spaces)
        words = text.split()
        return len(words)
    
    def get_absolute_url(self):
        """Get the absolute URL for this article."""
        return reverse('article-detail', kwargs={'slug': self.slug})
    
    def increment_views(self):
        """Increment the view count."""
        self.views_count += 1
        self.save(update_fields=['views_count'])
    
    def save_draft(self, draft_content):
        """Save draft content without changing publication status."""
        self.draft_content = draft_content
        self.save(update_fields=['draft_content', 'last_saved_at'])
    
    def get_editor_content(self):
        """Get the content that should be shown in the editor."""
        return self.draft_content or self.content
    
    @property
    def is_published(self):
        """Check if article is published."""
        return self.status == 'published'
    
    @property
    def has_draft_changes(self):
        """Check if there are unsaved draft changes."""
        return bool(self.draft_content and self.draft_content != self.content)


class Tag(TranslatableModel):
    """
    Tag model for article tagging with multilingual support.
    """
    
    translations = TranslatedFields(
        name=models.CharField(
            max_length=50,
            help_text='Tag name'
        ),
        slug=models.SlugField(
            max_length=50,
            unique=True,
            help_text='URL-friendly slug for tag'
        )
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'
        ordering = ['translations__name']
    
    def __str__(self):
        return self.safe_translation_getter('name', any_language=True) or f'Tag {self.pk}'
    
    def save(self, *args, **kwargs):
        # Only auto-generate slug if we have a translation with name
        if hasattr(self, 'name') and self.name and (not hasattr(self, 'slug') or not self.slug):
            try:
                self.slug = slugify(self.name)
            except:
                # If translation doesn't exist yet, skip slug generation
                pass
        super().save(*args, **kwargs)


class ArticleTag(models.Model):
    """
    Through model for Article-Tag relationship.
    """
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('article', 'tag')
        verbose_name = 'Article Tag'
        verbose_name_plural = 'Article Tags'
    
    def __str__(self):
        return f'{self.article} - {self.tag}'


# Add many-to-many relationship for tags
Article.add_to_class('tags', models.ManyToManyField(Tag, through=ArticleTag, related_name='articles', blank=True)) 