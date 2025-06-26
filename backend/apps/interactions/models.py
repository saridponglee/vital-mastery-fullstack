from django.db import models
from django.conf import settings
from apps.content.models import Article


class Comment(models.Model):
    """
    Comment model for article comments.
    """
    
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name='comments',
        help_text='Article this comment belongs to'
    )
    
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comments',
        help_text='Comment author'
    )
    
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies',
        help_text='Parent comment for threaded comments'
    )
    
    content = models.TextField(
        max_length=2000,
        help_text='Comment content'
    )
    
    is_approved = models.BooleanField(
        default=True,
        help_text='Whether the comment is approved for display'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'
        ordering = ['created_at']
    
    def __str__(self):
        return f'Comment by {self.author.username} on {self.article.title}'
    
    @property
    def is_reply(self):
        """Check if this comment is a reply to another comment."""
        return self.parent is not None
    
    def get_replies(self):
        """Get all approved replies to this comment."""
        return self.replies.filter(is_approved=True).order_by('created_at')


class Like(models.Model):
    """
    Like model for article likes.
    """
    
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name='likes',
        help_text='Article that was liked'
    )
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='likes',
        help_text='User who liked the article'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('article', 'user')
        verbose_name = 'Like'
        verbose_name_plural = 'Likes'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.user.username} likes {self.article.title}'


class Bookmark(models.Model):
    """
    Bookmark model for saving articles.
    """
    
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name='bookmarks',
        help_text='Article that was bookmarked'
    )
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='bookmarks',
        help_text='User who bookmarked the article'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('article', 'user')
        verbose_name = 'Bookmark'
        verbose_name_plural = 'Bookmarks'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.user.username} bookmarked {self.article.title}' 