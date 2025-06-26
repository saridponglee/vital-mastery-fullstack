from django.urls import path
from . import views

app_name = 'interactions'

urlpatterns = [
    # Comment endpoints
    path('articles/<slug:article_slug>/comments/', 
         views.ArticleCommentsView.as_view(), 
         name='article-comments'),
    
    # Like endpoints
    path('articles/<slug:article_slug>/like/', 
         views.article_like_view, 
         name='article-like'),
    
    # Interaction stats
    path('articles/<slug:article_slug>/interactions/', 
         views.article_interactions_view, 
         name='article-interactions'),
] 