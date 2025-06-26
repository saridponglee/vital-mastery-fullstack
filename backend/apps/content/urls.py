from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .sse_views import (
    ArticleSSEView, UserSSEView, GlobalSSEView, EditingSSEView,
    increment_view_count, get_article_stats,
    start_editing_session, update_cursor_position, 
    editing_heartbeat, end_editing_session, get_active_editors
)

app_name = 'content'

# DRF Router for ViewSets
router = DefaultRouter()
router.register(r'api/articles', views.ArticleViewSet, basename='articles')

urlpatterns = [
    # ViewSet routes
    path('', include(router.urls)),
    
    # Article endpoints
    path('articles/', views.ArticleListView.as_view(), name='article-list'),
    path('articles/<slug:slug>/', views.ArticleDetailView.as_view(), name='article-detail'),
    path('articles/create/', views.ArticleCreateView.as_view(), name='article-create'),
    path('articles/<slug:slug>/update/', views.ArticleUpdateView.as_view(), name='article-update'),
    
    # Special article views
    path('articles/popular/', views.PopularArticlesView.as_view(), name='popular-articles'),
    path('articles/recent/', views.RecentArticlesView.as_view(), name='recent-articles'),
    
    # Category endpoints
    path('categories/', views.CategoryListView.as_view(), name='category-list'),
    path('categories/<slug:slug>/', views.CategoryDetailView.as_view(), name='category-detail'),
    
    # Tag endpoints
    path('tags/', views.TagListView.as_view(), name='tag-list'),
    
    # Search endpoint
    path('search/', views.search_view, name='search'),
    
    # TinyMCE image upload
    path('tinymce/upload/', views.tinymce_upload_view, name='tinymce-upload'),
    
    # EventStream for real-time updates (legacy)
    path('events/', include('django_eventstream.urls'), {
        'channels': ['article-updates-th', 'article-updates-en']
    }),
    
    # New SSE endpoints with comprehensive real-time features
    path('sse/article/<int:article_id>/', ArticleSSEView.as_view(), name='article-sse'),
    path('sse/user/', UserSSEView.as_view(), name='user-sse'),
    path('sse/global/', GlobalSSEView.as_view(), name='global-sse'),
    path('sse/editing/<int:article_id>/', EditingSSEView.as_view(), name='editing-sse'),
    
    # Real-time API endpoints
    path('articles/<int:article_id>/increment-views/', increment_view_count, name='increment-views'),
    path('articles/<int:article_id>/stats/', get_article_stats, name='article-stats'),
    
    # Collaborative editing endpoints
    path('articles/<int:article_id>/editing/start/', start_editing_session, name='start-editing'),
    path('articles/<int:article_id>/editing/cursor/', update_cursor_position, name='update-cursor'),
    path('articles/<int:article_id>/editing/heartbeat/', editing_heartbeat, name='editing-heartbeat'),
    path('articles/<int:article_id>/editing/end/', end_editing_session, name='end-editing'),
    path('articles/<int:article_id>/editing/active/', get_active_editors, name='active-editors'),
] 