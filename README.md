# VITAL MASTERY

A modern, Thai-focused content platform built with Django and React, featuring a clean Medium-like design with iOS aesthetics.

## 🚀 Features

### Content Management
- **Multilingual Support**: Full Thai and English content support using django-parler
- **Rich Text Editor**: TinyMCE integration with Thai language support and image uploads
- **Article Management**: Create, edit, and publish articles with categories and tags
- **SEO Optimized**: Dynamic meta tags, sitemaps, and structured data

### User Experience
- **Mobile-First Design**: Responsive design optimized for touch interfaces
- **Eye-Friendly Reading**: Typography optimized for comfort with 21px base font and 1.58 line height
- **Clean Aesthetics**: Medium-inspired layout with iOS design principles
- **Thai Language Optimized**: Proper Thai text rendering and font selection

### Technical Features
- **Hybrid Architecture**: React SPA served by Django for optimal SEO
- **REST API**: Django REST Framework with comprehensive endpoints
- **Authentication**: Session-based authentication with CSRF protection
- **Search**: Advanced search functionality for Thai content
- **Performance**: Optimized with lazy loading and code splitting

## 🛠 Technology Stack

### Backend
- **Django 5.0.3** - Web framework
- **Django REST Framework 3.14** - API framework
- **PostgreSQL** - Database (with UTF-8 Thai support)
- **django-parler** - Multilingual content management
- **TinyMCE** - Rich text editor

### Frontend
- **React 18** - UI library
- **TypeScript** - Static typing
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Styling framework
- **React Router** - Client-side routing
- **Zustand** - State management

## 📋 Prerequisites

- Python 3.9+
- Node.js 18+
- PostgreSQL 14+
- Git

## 🚀 Installation & Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd Vital-Mastery-Fullstack
```

### 2. Environment Setup

Copy the environment template:
```bash
cp env.example .env
```

The `.env` file includes:
- Django Secret Key: `vk2@x8h9*d&f$m4n7p-w+q5t3r6y8u1i0o2k5j7h9g3f4d6s1a8z`
- TinyMCE API Key: `wl4p3hpruyc1h75fgou8wnm83zmvosve1jkmqo4u3kecci46`

### 3. Database Setup

Create PostgreSQL database:
```bash
createdb vital_mastery_db
```

Update the `DATABASE_URL` in your `.env` file:
```
DATABASE_URL=postgresql://your_username:your_password@localhost:5432/vital_mastery_db
```

### 4. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files (for production)
python manage.py collectstatic --noinput
```

### 5. Frontend Setup

```bash
# Navigate to frontend directory
cd ../frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### 6. Start Development Servers

**Terminal 1 - Django Backend:**
```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
python manage.py runserver
```

**Terminal 2 - React Frontend:**
```bash
cd frontend
npm run dev
```

## 🌐 Access the Application

- **Website**: http://localhost:3000
- **Django Admin**: http://localhost:8000/admin
- **API Documentation**: http://localhost:8000/api/v1/

## 📝 Usage

### Content Management

1. **Access Admin Panel**:
   - Go to http://localhost:8000/admin
   - Login with your superuser credentials

2. **Create Categories**:
   - Navigate to Content → Categories
   - Add categories in both Thai and English

3. **Create Articles**:
   - Navigate to Content → Articles
   - Use TinyMCE editor for rich content
   - Add Thai and English translations
   - Upload featured images

4. **Manage Users**:
   - Navigate to Users → Users
   - Set `is_author = True` for content creators

### Frontend Features

- **Homepage**: Overview of recent articles
- **Articles Page**: List all published articles with search and filtering
- **Article Detail**: Full article view with reading time and interactions
- **Categories**: Browse articles by category
- **Responsive Design**: Optimized for all device sizes

## 🔧 API Endpoints

### Articles
- `GET /api/v1/articles/` - List articles
- `GET /api/v1/articles/{slug}/` - Get article detail
- `POST /api/v1/articles/` - Create article (authenticated)
- `PUT /api/v1/articles/{slug}/` - Update article (author only)

### Categories
- `GET /api/v1/categories/` - List categories
- `GET /api/v1/categories/{slug}/` - Get category detail

### Authentication
- `POST /api/v1/auth/login/` - User login
- `POST /api/v1/auth/logout/` - User logout
- `GET /api/v1/auth/session/` - Check session status

### Search
- `GET /api/v1/search/?q={query}` - Search articles
- `GET /api/v1/search/?category={slug}` - Filter by category

## 🏗 Project Structure

```
Vital-Mastery-Fullstack/
├── backend/                 # Django backend
│   ├── vital_mastery/       # Project configuration
│   │   ├── settings/        # Environment-specific settings
│   │   └── urls.py          # Main URL configuration
│   ├── apps/                # Django applications
│   │   ├── users/           # User management
│   │   ├── content/         # Articles, categories, tags
│   │   └── interactions/    # Comments, likes
│   ├── templates/           # Django templates
│   ├── static/              # Static files
│   └── requirements.txt     # Python dependencies
├── frontend/                # React frontend
│   ├── src/                 # Source code
│   │   ├── components/      # Reusable components
│   │   ├── pages/           # Page components
│   │   ├── hooks/           # Custom hooks
│   │   ├── services/        # API services
│   │   └── types/           # TypeScript types
│   ├── package.json         # Node.js dependencies
│   └── vite.config.ts       # Vite configuration
└── .env                     # Environment variables
```

## 🔒 Security Features

- **CSRF Protection**: Built-in Django CSRF protection
- **Authentication**: Session-based authentication
- **Input Validation**: Comprehensive data validation
- **XSS Protection**: Content sanitization
- **File Upload Security**: Type and size validation

## 🌍 Internationalization

The platform supports both Thai and English:

- **Backend**: django-parler for model translations
- **Frontend**: Thai fonts and proper text rendering
- **Content**: Bilingual article management
- **UI**: Thai language interface elements

## 🚀 Production Deployment

### Build Frontend
```bash
cd frontend
npm run build
```

### Configure Django for Production
```bash
cd backend
export DJANGO_SETTINGS_MODULE=vital_mastery.settings.production
python manage.py collectstatic --noinput
```

### Environment Variables for Production
```env
DEBUG=False
DJANGO_SETTINGS_MODULE=vital_mastery.settings.production
DATABASE_URL=postgresql://user:pass@host:port/db
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 License

This project is licensed under the MIT License.

## 🐛 Troubleshooting

### Common Issues

1. **Database Connection Error**:
   - Ensure PostgreSQL is running
   - Check DATABASE_URL in .env file
   - Verify database exists

2. **Frontend Build Errors**:
   - Clear node_modules: `rm -rf node_modules && npm install`
   - Check Node.js version compatibility

3. **Thai Font Issues**:
   - Ensure Google Fonts are loading
   - Check internet connection for font CDN

4. **TinyMCE Not Loading**:
   - Verify TinyMCE API key in .env
   - Check CORS settings for TinyMCE CDN

### Development Tips

- Use Django Debug Toolbar for backend debugging
- Enable React Developer Tools for frontend debugging
- Check browser console for JavaScript errors
- Monitor Django logs for backend issues

## 📞 Support

For support, please create an issue in the repository or contact the development team.

---

Built with ❤️ for the Thai content community 