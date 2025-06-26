from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db.models import Q, Count
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from rest_framework import generics, filters, permissions, status, viewsets
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
import json

from .models import Article, Category, Tag
from .serializers import (
    ArticleListSerializer, ArticleDetailSerializer, 
    ArticleCreateUpdateSerializer, CategorySerializer, 
    TagSerializer, CategorySimpleSerializer, TagSimpleSerializer
)


class StandardResultsSetPagination(PageNumberPagination):
    """
    Custom pagination class for API results.
    """
    page_size = 12
    page_size_query_param = 'page_size'
    max_page_size = 50


class ArticleFilter:
    """
    Custom filter class for articles.
    """
    @staticmethod
    def filter_by_search(queryset, search_term):
        """Filter articles by search term in title and content."""
        if not search_term:
            return queryset
        
        return queryset.filter(
            Q(translations__title__icontains=search_term) |
            Q(translations__content__icontains=search_term) |
            Q(translations__excerpt__icontains=search_term)
        ).distinct()
    
    @staticmethod
    def filter_by_category(queryset, category_slug):
        """Filter articles by category slug."""
        if not category_slug:
            return queryset
        
        return queryset.filter(
            category__translations__slug=category_slug
        )
    
    @staticmethod
    def filter_by_tag(queryset, tag_slug):
        """Filter articles by tag slug."""
        if not tag_slug:
            return queryset
        
        return queryset.filter(
            tags__translations__slug=tag_slug
        )


class ArticleListView(generics.ListAPIView):
    """
    List published articles with search and filtering.
    """
    serializer_class = ArticleListSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    ordering_fields = ['created_at', 'published_at', 'views_count', 'reading_time']
    ordering = ['-published_at']
    
    def get_queryset(self):
        """
        Get queryset with proper filtering and optimization.
        """
        queryset = Article.objects.filter(
            status='published'
        ).select_related(
            'author', 'category'
        ).prefetch_related(
            'tags', 'translations'
        )
        
        # Apply custom filters
        search = self.request.query_params.get('search', None)
        category = self.request.query_params.get('category', None)
        tag = self.request.query_params.get('tag', None)
        
        if search:
            queryset = ArticleFilter.filter_by_search(queryset, search)
        
        if category:
            queryset = ArticleFilter.filter_by_category(queryset, category)
        
        if tag:
            queryset = ArticleFilter.filter_by_tag(queryset, tag)
        
        return queryset


class ArticleDetailView(generics.RetrieveAPIView):
    """
    Retrieve a single article by slug.
    """
    serializer_class = ArticleDetailSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'translations__slug'
    lookup_url_kwarg = 'slug'
    
    def get_queryset(self):
        """Get optimized queryset for article detail."""
        return Article.objects.filter(
            status='published'
        ).select_related(
            'author', 'category'
        ).prefetch_related(
            'tags', 'translations'
        )
    
    def get_object(self):
        """Get article and increment views."""
        obj = super().get_object()
        obj.increment_views()
        return obj


class ArticleCreateView(generics.CreateAPIView):
    """
    Create a new article (admin only).
    """
    serializer_class = ArticleCreateUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        """Set the author to the current user."""
        serializer.save(author=self.request.user)


class ArticleUpdateView(generics.UpdateAPIView):
    """
    Update an existing article (author or admin only).
    """
    serializer_class = ArticleCreateUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'translations__slug'
    lookup_url_kwarg = 'slug'
    
    def get_queryset(self):
        """Get articles that the user can edit."""
        user = self.request.user
        if user.is_superuser or user.is_staff:
            return Article.objects.all()
        return Article.objects.filter(author=user)


class CategoryListView(generics.ListAPIView):
    """
    List all categories with article counts.
    """
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        """Get categories with published articles."""
        return Category.objects.annotate(
            published_articles_count=Count(
                'articles', 
                filter=Q(articles__status='published')
            )
        ).filter(
            published_articles_count__gt=0
        ).order_by('translations__name')


class CategoryDetailView(generics.RetrieveAPIView):
    """
    Retrieve a single category by slug.
    """
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'translations__slug'
    lookup_url_kwarg = 'slug'
    
    def get_queryset(self):
        return Category.objects.all()


class TagListView(generics.ListAPIView):
    """
    List all tags.
    """
    serializer_class = TagSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        """Get tags with published articles."""
        return Tag.objects.annotate(
            published_articles_count=Count(
                'articles', 
                filter=Q(articles__status='published')
            )
        ).filter(
            published_articles_count__gt=0
        ).order_by('translations__name')


class PopularArticlesView(generics.ListAPIView):
    """
    List popular articles based on views.
    """
    serializer_class = ArticleListSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        """Get most viewed published articles."""
        return Article.objects.filter(
            status='published'
        ).select_related(
            'author', 'category'
        ).prefetch_related(
            'tags'
        ).order_by('-views_count', '-published_at')


class RecentArticlesView(generics.ListAPIView):
    """
    List recent articles.
    """
    serializer_class = ArticleListSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        """Get recently published articles."""
        return Article.objects.filter(
            status='published'
        ).select_related(
            'author', 'category'
        ).prefetch_related(
            'tags'
        ).order_by('-published_at')[:10]


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
@csrf_exempt
def tinymce_upload_view(request):
    """
    Handle TinyMCE image uploads.
    """
    if request.method == 'POST' and request.FILES.get('file'):
        uploaded_file = request.FILES['file']
        
        # Validate file type
        allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
        if uploaded_file.content_type not in allowed_types:
            return JsonResponse({
                'error': 'File type not allowed. Please upload JPEG, PNG, GIF, or WebP images.'
            }, status=400)
        
        # Validate file size (5MB max)
        if uploaded_file.size > 5 * 1024 * 1024:
            return JsonResponse({
                'error': 'File size too large. Maximum size is 5MB.'
            }, status=400)
        
        # Save file
        import os
        import uuid
        from django.conf import settings
        from django.core.files.storage import default_storage
        
        # Generate unique filename
        file_extension = os.path.splitext(uploaded_file.name)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = f"tinymce/{unique_filename}"
        
        # Save file
        saved_path = default_storage.save(file_path, uploaded_file)
        file_url = default_storage.url(saved_path)
        
        # Build absolute URL
        full_url = request.build_absolute_uri(file_url)
        
        return JsonResponse({
            'location': full_url
        })
    
    return JsonResponse({
        'error': 'No file uploaded'
    }, status=400)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def search_view(request):
    """
    Advanced search endpoint for articles.
    """
    query = request.query_params.get('q', '').strip()
    category_slug = request.query_params.get('category', '')
    tag_slug = request.query_params.get('tag', '')
    
    if not query and not category_slug and not tag_slug:
        return Response({
            'results': [],
            'count': 0,
            'message': 'Please provide a search query, category, or tag.'
        })
    
    # Start with published articles
    articles = Article.objects.filter(status='published')
    
    # Apply filters
    if query:
        articles = ArticleFilter.filter_by_search(articles, query)
    
    if category_slug:
        articles = ArticleFilter.filter_by_category(articles, category_slug)
    
    if tag_slug:
        articles = ArticleFilter.filter_by_tag(articles, tag_slug)
    
    # Optimize query
    articles = articles.select_related(
        'author', 'category'
    ).prefetch_related(
        'tags'
    ).order_by('-published_at')
    
    # Paginate results
    paginator = StandardResultsSetPagination()
    page = paginator.paginate_queryset(articles, request)
    
    if page is not None:
        serializer = ArticleListSerializer(page, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data)
    
    serializer = ArticleListSerializer(articles, many=True, context={'request': request})
    return Response({
        'results': serializer.data,
        'count': len(serializer.data)
    })


class ArticleViewSet(viewsets.ModelViewSet):
    """
    ViewSet for real-time article management.
    """
    serializer_class = ArticleDetailSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        """Get articles based on user permissions."""
        return Article.objects.filter(status='published').order_by('-published_at')
    
    @action(detail=False, methods=['get'])
    def latest(self, request):
        """Get latest published articles with caching."""
        cache_key = f'latest_articles_{request.LANGUAGE_CODE}'
        cached_articles = cache.get(cache_key)
        
        if cached_articles is None:
            articles = self.get_queryset()[:10]
            serializer = self.get_serializer(articles, many=True)
            cached_articles = serializer.data
            cache.set(cache_key, cached_articles, 300)  # Cache for 5 minutes
        
        return Response(cached_articles)
    
    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """Get articles by category."""
        category_slug = request.query_params.get('category')
        if not category_slug:
            return Response({'error': 'Category slug is required'}, status=400)
        
        articles = self.get_queryset().filter(
            category__translations__slug=category_slug
        )
        
        page = self.paginate_queryset(articles)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(articles, many=True)
        return Response(serializer.data)
    
    def list(self, request, *args, **kwargs):
        """Enhanced list method with caching."""
        cache_key = f'article_list_{request.LANGUAGE_CODE}_{request.GET.urlencode()}'
        cached_response = cache.get(cache_key)
        
        if cached_response is None:
            response = super().list(request, *args, **kwargs)
            cache.set(cache_key, response.data, 300)  # Cache for 5 minutes
            return response
        
        return Response(cached_response) 