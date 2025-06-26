from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils.text import slugify
from parler.models import TranslatableModel, TranslatedFields
from tinymce.models import HTMLField
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
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Article(TranslatableModel):
    """
    Article model with multilingual content support.
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
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)
    
    # Translatable fields
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
        content=HTMLField(
            help_text='Main article content (HTML)'
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
    
    def __str__(self):
        title = self.safe_translation_getter('title', any_language=True)
        return title or f'Article {self.pk}'
    
    def save(self, *args, **kwargs):
        # Auto-generate slug from title if not provided
        if not self.slug and hasattr(self, 'title'):
            self.slug = slugify(self.title)
        
        # Calculate reading time based on content
        if hasattr(self, 'content') and self.content:
            word_count = self.get_word_count()
            self.reading_time = max(1, word_count // 250)  # Assume 250 words per minute
        
        # Set published_at when status changes to published
        if self.status == 'published' and not self.published_at:
            from django.utils import timezone
            self.published_at = timezone.now()
        
        super().save(*args, **kwargs)
    
    def get_word_count(self):
        """Calculate word count from content (removing HTML tags)."""
        if not hasattr(self, 'content') or not self.content:
            return 0
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', self.content)
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
    
    @property
    def is_published(self):
        """Check if article is published."""
        return self.status == 'published'


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
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


# Many-to-many relationship for article tags
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

# Add tags relationship to Article
Article.add_to_class(
    'tags',
    models.ManyToManyField(
        Tag,
        through=ArticleTag,
        blank=True,
        related_name='articles',
        help_text='Tags for this article'
    )
) 