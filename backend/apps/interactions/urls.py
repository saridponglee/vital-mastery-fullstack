from django.urls import path
from . import views

app_name = 'interactions'

urlpatterns = [
    # Comment endpoints with real-time support
    path('articles/<slug:article_slug>/comments/', 
         views.ArticleCommentsView.as_view(), 
         name='article-comments'),
    
    # Like endpoints with real-time support
    path('articles/<slug:article_slug>/like/', 
         views.article_like_view, 
         name='article-like'),
    
    # Bookmark endpoints
    path('articles/<slug:article_slug>/bookmark/', 
         views.article_bookmark_view, 
         name='article-bookmark'),
    
    # Real-time interaction stats
    path('articles/<slug:article_slug>/interactions/', 
         views.article_interactions_view, 
         name='article-interactions'),
] 