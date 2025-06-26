from rest_framework import serializers
from parler_rest.serializers import TranslatableModelSerializer, TranslatedFieldsField
from parler_rest.fields import TranslatedField
from apps.users.serializers import UserSerializer
from .models import Article, Category, Tag


class CategorySerializer(TranslatableModelSerializer):
    """
    Serializer for Category model with multilingual support.
    """
    translations = TranslatedFieldsField(shared_model=Category)
    article_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = (
            'id', 'translations', 'article_count', 
            'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at', 'article_count')
    
    def get_article_count(self, obj):
        """Get the number of published articles in this category."""
        return obj.articles.filter(status='published').count()


class CategorySimpleSerializer(serializers.ModelSerializer):
    """
    Simple category serializer for nested use.
    """
    name = TranslatedField()
    slug = TranslatedField()
    
    class Meta:
        model = Category
        fields = ('id', 'name', 'slug')


class TagSerializer(TranslatableModelSerializer):
    """
    Serializer for Tag model with multilingual support.
    """
    translations = TranslatedFieldsField(shared_model=Tag)
    
    class Meta:
        model = Tag
        fields = ('id', 'translations', 'created_at')
        read_only_fields = ('id', 'created_at')


class TagSimpleSerializer(serializers.ModelSerializer):
    """
    Simple tag serializer for nested use.
    """
    name = TranslatedField()
    slug = TranslatedField()
    
    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class ArticleListSerializer(TranslatableModelSerializer):
    """
    Serializer for Article list view with essential information.
    """
    translations = TranslatedFieldsField(shared_model=Article)
    author = UserSerializer(read_only=True)
    category = CategorySimpleSerializer(read_only=True)
    tags = TagSimpleSerializer(many=True, read_only=True)
    featured_image_url = serializers.SerializerMethodField()
    reading_time_text = serializers.SerializerMethodField()
    
    class Meta:
        model = Article
        fields = (
            'id', 'translations', 'author', 'category', 'tags',
            'featured_image_url', 'reading_time', 'reading_time_text',
            'views_count', 'status', 'created_at', 'published_at'
        )
        read_only_fields = (
            'id', 'author', 'views_count', 'created_at', 'published_at'
        )
    
    def get_featured_image_url(self, obj):
        """Get the full URL for the featured image."""
        if obj.featured_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.featured_image.url)
            return obj.featured_image.url
        return None
    
    def get_reading_time_text(self, obj):
        """Get formatted reading time text."""
        if obj.reading_time == 1:
            return f'{obj.reading_time} minute read'
        return f'{obj.reading_time} minutes read'


class ArticleDetailSerializer(TranslatableModelSerializer):
    """
    Detailed serializer for Article model with full content.
    """
    translations = TranslatedFieldsField(shared_model=Article)
    author = UserSerializer(read_only=True)
    category = CategorySimpleSerializer(read_only=True)
    tags = TagSimpleSerializer(many=True, read_only=True)
    featured_image_url = serializers.SerializerMethodField()
    reading_time_text = serializers.SerializerMethodField()
    related_articles = serializers.SerializerMethodField()
    
    class Meta:
        model = Article
        fields = (
            'id', 'translations', 'author', 'category', 'tags',
            'featured_image_url', 'reading_time', 'reading_time_text',
            'views_count', 'status', 'created_at', 'updated_at', 
            'published_at', 'related_articles'
        )
        read_only_fields = (
            'id', 'author', 'views_count', 'created_at', 
            'updated_at', 'published_at', 'related_articles'
        )
    
    def get_featured_image_url(self, obj):
        """Get the full URL for the featured image."""
        if obj.featured_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.featured_image.url)
            return obj.featured_image.url
        return None
    
    def get_reading_time_text(self, obj):
        """Get formatted reading time text."""
        if obj.reading_time == 1:
            return f'{obj.reading_time} minute read'
        return f'{obj.reading_time} minutes read'
    
    def get_related_articles(self, obj):
        """Get related articles from the same category."""
        if not obj.category:
            return []
        
        related = Article.objects.filter(
            category=obj.category,
            status='published'
        ).exclude(id=obj.id)[:3]
        
        return ArticleListSerializer(
            related, 
            many=True, 
            context=self.context
        ).data


class ArticleCreateUpdateSerializer(TranslatableModelSerializer):
    """
    Serializer for creating and updating articles.
    """
    translations = TranslatedFieldsField(shared_model=Article)
    tag_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        help_text='List of tag IDs to associate with this article'
    )
    
    class Meta:
        model = Article
        fields = (
            'id', 'translations', 'category', 'featured_image',
            'status', 'tag_ids', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')
    
    def create(self, validated_data):
        """Create article with tags."""
        tag_ids = validated_data.pop('tag_ids', [])
        article = super().create(validated_data)
        
        if tag_ids:
            tags = Tag.objects.filter(id__in=tag_ids)
            article.tags.set(tags)
        
        return article
    
    def update(self, instance, validated_data):
        """Update article with tags."""
        tag_ids = validated_data.pop('tag_ids', None)
        article = super().update(instance, validated_data)
        
        if tag_ids is not None:
            tags = Tag.objects.filter(id__in=tag_ids)
            article.tags.set(tags)
        
        return article 