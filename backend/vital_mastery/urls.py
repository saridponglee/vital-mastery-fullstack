"""
URL configuration for VITAL MASTERY project.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    # Admin interface
    path('admin/', admin.site.urls),
    
    # API endpoints
    path('api/v1/', include('apps.content.urls')),
    path('api/v1/', include('apps.interactions.urls')),
    path('api/v1/', include('apps.users.urls')),
    
    # TinyMCE
    path('tinymce/', include('tinymce.urls')),
    
    # Frontend SPA - catch all routes
    path('', TemplateView.as_view(template_name='index.html'), name='home'),
    path('articles/', TemplateView.as_view(template_name='index.html'), name='articles'),
    path('articles/<slug:slug>/', TemplateView.as_view(template_name='index.html'), name='article-detail'),
    path('category/<slug:slug>/', TemplateView.as_view(template_name='index.html'), name='category'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += staticfiles_urlpatterns()
    
    # Debug toolbar
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar
        urlpatterns = [
            path('__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns

# Admin site configuration
admin.site.site_header = 'VITAL MASTERY Administration'
admin.site.site_title = 'VITAL MASTERY Admin'
admin.site.index_title = 'Welcome to VITAL MASTERY Administration' 