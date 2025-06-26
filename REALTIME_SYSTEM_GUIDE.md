# Real-Time Article Publishing System Implementation Guide

## Overview

This document provides a comprehensive guide for the real-time article publishing system implemented in VITAL MASTERY. The system uses Server-Sent Events (SSE) with django-eventstream to provide automatic article updates from Django admin to the React frontend.

## Architecture

The real-time system consists of:

1. **Backend (Django)**: 
   - Django signals that trigger when articles are published
   - django-eventstream for SSE functionality
   - Redis for scaling (optional)
   - Enhanced Django admin with real-time publishing actions

2. **Frontend (React)**:
   - Custom SSE hook for real-time connections
   - Zustand store for state management
   - Automatic UI updates when articles are published
   - Language switching support (Thai/English)

## Features Implemented

### Backend Features

- ✅ Real-time article publishing notifications
- ✅ Multilingual support (Thai/English) with django-parler
- ✅ Enhanced Django admin with publishing actions
- ✅ Database indexes for performance optimization
- ✅ Redis caching for article lists
- ✅ ASGI configuration with Daphne
- ✅ Signal-based event broadcasting

### Frontend Features

- ✅ Server-Sent Events integration
- ✅ Real-time article list updates
- ✅ Connection status indicator
- ✅ Language switching
- ✅ Automatic reconnection
- ✅ Modern UI with Tailwind CSS
- ✅ Performance optimizations with caching

## Quick Start

### 1. Install Dependencies

Backend:
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

Frontend:
```bash
cd frontend
npm install
```

### 2. Set Up Environment

Create a `.env` file in the project root:
```env
# Django Settings
DJANGO_SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=sqlite:///db.sqlite3

# Redis (optional, for scaling)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### 3. Run Migrations

```bash
cd backend
source venv/bin/activate
venv/bin/python manage.py migrate
```

### 4. Create Superuser

```bash
venv/bin/python manage.py createsuperuser
```

### 5. Start the Development Servers

Terminal 1 - Django (ASGI):
```bash
cd backend
source venv/bin/activate
venv/bin/python manage.py runserver
```

Terminal 2 - React:
```bash
cd frontend
npm run dev
```

## Testing the Real-Time System

### Step 1: Access the Applications

1. Django Admin: http://localhost:8000/admin/
2. React Frontend: http://localhost:3000/

### Step 2: Test Real-Time Publishing

1. **Open Multiple Browser Windows**:
   - Window 1: React frontend (http://localhost:3000/articles)
   - Window 2: Django admin (http://localhost:8000/admin/)

2. **Create and Publish an Article**:
   - In Django admin, go to Content → Articles
   - Click "Add Article"
   - Fill in the required fields:
     - Title (both English and Thai)
     - Content (using the prose editor)
     - Author (select yourself)
     - Status: Set to "Draft" initially
   - Save the article

3. **Test Real-Time Publishing**:
   - Change the article status from "Draft" to "Published"
   - Save the article
   - **Check React frontend**: The article should appear automatically without page refresh
   - **Check connection status**: Should show "Live Updates" with a green dot

4. **Test Language Switching**:
   - In React frontend, click the language switcher (English/ไทย)
   - Articles should update to show the selected language version

### Step 3: Test Bulk Publishing

1. Create multiple draft articles in Django admin
2. Select multiple articles in the admin list
3. Choose "Publish selected articles (triggers real-time updates)" from Actions dropdown
4. Click "Go"
5. All articles should appear in React frontend immediately

## API Endpoints

### REST API
- `GET /api/content/api/articles/` - List articles (with caching)
- `GET /api/content/api/articles/latest/` - Get latest articles
- `GET /api/content/api/articles/by_category/?category=slug` - Filter by category

### Real-Time Endpoints
- `/api/content/events/article-updates-en/` - English article updates
- `/api/content/events/article-updates-th/` - Thai article updates

## File Structure

```
Vital-Mastery-Fullstack/
├── backend/
│   ├── apps/content/
│   │   ├── models.py          # Enhanced Article model with indexes
│   │   ├── signals.py         # Real-time publishing signals
│   │   ├── admin.py           # Enhanced admin with publishing actions
│   │   ├── views.py           # API views with caching
│   │   └── urls.py            # URL routing with SSE endpoints
│   ├── vital_mastery/
│   │   ├── settings/base.py   # Django settings with EventStream
│   │   └── asgi.py            # ASGI configuration
│   └── requirements.txt       # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── hooks/useSSE.ts           # SSE custom hook
│   │   ├── stores/articleStore.ts    # Zustand store
│   │   ├── components/
│   │   │   ├── ArticleList.tsx       # Real-time article list
│   │   │   └── LanguageSwitcher.tsx  # Language switcher
│   │   └── pages/ArticlesPage.tsx    # Updated articles page
│   ├── vite.config.ts         # Vite config with SSE proxy
│   └── package.json           # Frontend dependencies
└── REALTIME_SYSTEM_GUIDE.md  # This guide
```

## Configuration Details

### Django Settings (backend/vital_mastery/settings/base.py)

Key configurations added:
```python
# ASGI Application
ASGI_APPLICATION = 'vital_mastery.asgi.application'

# EventStream Configuration
EVENTSTREAM_REDIS = {
    'host': env('REDIS_HOST', default='localhost'),
    'port': env('REDIS_PORT', default=6379),
    'db': env('REDIS_DB', default=0),
}

# Cache Configuration
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': f"redis://{EVENTSTREAM_REDIS['host']}:{EVENTSTREAM_REDIS['port']}/1",
    }
}
```

### React Configuration (frontend/vite.config.ts)

SSE proxy configuration:
```typescript
'/events': {
  target: 'http://localhost:8000',
  changeOrigin: true,
  secure: false,
  configure: (proxy) => {
    proxy.on('proxyReq', (proxyReq) => {
      proxyReq.setHeader('Cache-Control', 'no-cache');
      proxyReq.setHeader('Accept', 'text/event-stream');
    });
  },
}
```

## Troubleshooting

### Common Issues

1. **SSE Connection Fails**:
   - Check if Django server is running
   - Verify Vite proxy configuration
   - Check browser console for errors

2. **Real-Time Updates Not Working**:
   - Verify signals are properly connected (`apps.py` ready method)
   - Check Django logs for signal execution
   - Ensure EventStream tables are migrated

3. **Language Switching Issues**:
   - Verify Parler translations exist for articles
   - Check language configuration in Django settings
   - Ensure both languages are properly saved in admin

4. **Performance Issues**:
   - Enable Redis caching
   - Check database indexes are created
   - Monitor connection counts in production

### Debug Mode

Enable verbose SSE logging by adding to Django settings:
```python
LOGGING = {
    'loggers': {
        'django_eventstream': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

## Production Deployment

### Nginx Configuration
```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location /events/ {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Connection "";
        proxy_buffering off;
        proxy_cache off;
        proxy_read_timeout 86400;
    }

    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
    }

    location / {
        root /var/www/vitalmastery/dist;
        try_files $uri $uri/ /index.html;
    }
}
```

### Systemd Service
```ini
[Unit]
Description=Vital Mastery Daphne Server
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/vitalmastery
ExecStart=/var/www/vitalmastery/venv/bin/daphne -b 0.0.0.0 -p 8000 vitalmastery.asgi:application
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

## Performance Considerations

1. **Database Optimization**:
   - Indexes on (status, published_at) for fast queries
   - Select_related and prefetch_related in ViewSets
   - Pagination for large article lists

2. **Caching Strategy**:
   - Redis cache for article lists (5-minute TTL)
   - Cache invalidation on article status changes
   - Language-specific cache keys

3. **Scaling**:
   - Redis for EventStream channel layer
   - Multiple Daphne instances behind load balancer
   - CDN for static assets

## Security Considerations

1. **CORS Configuration**: Restrict allowed origins
2. **Rate Limiting**: Implement connection limits per IP
3. **Authentication**: Secure SSE endpoints with session auth
4. **Content Security**: django-prose-editor sanitizes content

## Monitoring

- **Connection Health**: Track SSE connection counts
- **Event Volume**: Monitor event publishing frequency
- **Performance**: Database query times and cache hit rates
- **Errors**: SSE disconnections and reconnection attempts

## Future Enhancements

- [ ] Push notifications for mobile devices
- [ ] Article draft collaboration
- [ ] Real-time comment updates
- [ ] User presence indicators
- [ ] Article view counters
- [ ] Advanced filtering and search
- [ ] Analytics dashboard for real-time metrics

## Support

For issues or questions about the real-time system:

1. Check this guide first
2. Review Django and React console logs
3. Test with multiple browser windows
4. Verify all dependencies are installed correctly

The system is designed to be robust with automatic reconnection and error handling, providing a seamless real-time experience for content management and consumption. 