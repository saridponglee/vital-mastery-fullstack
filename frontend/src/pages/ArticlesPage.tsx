import React from 'react'
import { ArticleList } from '../components/ArticleList'
import { LanguageSwitcher } from '../components/LanguageSwitcher'

const ArticlesPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header with Language Switcher */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Real-Time Articles</h1>
              <p className="text-gray-600 mt-1">
                Live updates from VITAL MASTERY content management system
              </p>
            </div>
            <LanguageSwitcher />
          </div>
        </div>
      </div>

      {/* Real-Time Article List */}
      <ArticleList />
    </div>
  )
}

export default ArticlesPage 