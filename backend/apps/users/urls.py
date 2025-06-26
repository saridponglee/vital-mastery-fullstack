from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    # Authentication endpoints
    path('auth/login/', views.login_view, name='login'),
    path('auth/logout/', views.logout_view, name='logout'),
    path('auth/session/', views.session_view, name='session'),
    path('auth/register/', views.register_view, name='register'),
    
    # User profile endpoints
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    
    # Authors list
    path('authors/', views.AuthorListView.as_view(), name='authors'),
] 