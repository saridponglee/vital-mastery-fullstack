#!/bin/bash

# VITAL MASTERY Setup Script
echo "🚀 Setting up VITAL MASTERY..."

# Check if we're in the right directory
if [ ! -f "env.example" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📋 Creating .env file..."
    cp env.example .env
    echo "✅ .env file created with default settings"
else
    echo "📋 .env file already exists"
fi

# Setup Backend
echo "🔧 Setting up Django backend..."
cd backend

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "🐍 Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Check if database exists, if not create it
echo "💾 Setting up database..."
python manage.py check

# Run migrations
echo "🔄 Running database migrations..."
python manage.py migrate

# Create static directory
mkdir -p static

echo "✅ Backend setup complete!"

# Setup Frontend
cd ../frontend
echo "🎨 Setting up React frontend..."

# Install dependencies
echo "📦 Installing Node.js dependencies..."
npm install

echo "✅ Frontend setup complete!"

# Return to root directory
cd ..

echo ""
echo "🎉 VITAL MASTERY setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Create a superuser:"
echo "   cd backend && source venv/bin/activate && python manage.py createsuperuser"
echo ""
echo "2. Start the development servers:"
echo "   Terminal 1: cd backend && source venv/bin/activate && python manage.py runserver"
echo "   Terminal 2: cd frontend && npm run dev"
echo ""
echo "3. Access the application:"
echo "   Website: http://localhost:3000"
echo "   Django Admin: http://localhost:8000/admin"
echo ""
echo "📖 For detailed instructions, see README.md"
echo ""
echo "🛠 Environment variables are already configured with:"
echo "   - Django Secret Key: vk2@x8h9*d&f$m4n7p-w+q5t3r6y8u1i0o2k5j7h9g3f4d6s1a8z"
echo "   - TinyMCE API Key: wl4p3hpruyc1h75fgou8wnm83zmvosve1jkmqo4u3kecci46"
echo "" 