from django.urls import path
from . import views

app_name = 'content'

urlpatterns = [
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
] 