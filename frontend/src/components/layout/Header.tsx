import React from 'react'
import { Link } from 'react-router-dom'

const Header: React.FC = () => {
  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <div className="flex-shrink-0">
            <Link to="/" className="text-2xl font-bold text-gray-900 hover:text-gray-700">
              VITAL MASTERY
            </Link>
          </div>

          {/* Navigation */}
          <nav className="hidden md:flex space-x-8">
            <Link 
              to="/" 
              className="text-gray-600 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium transition-colors"
            >
              หน้าแรก
            </Link>
            <Link 
              to="/articles" 
              className="text-gray-600 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium transition-colors"
            >
              บทความ
            </Link>
          </nav>

          {/* Mobile menu button */}
          <div className="md:hidden">
            <button className="text-gray-600 hover:text-gray-900 focus:outline-none focus:text-gray-900">
              <svg className="h-6 w-6" stroke="currentColor" fill="none" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </header>
  )
}

export default Header 