import React from 'react'
import { useParams } from 'react-router-dom'

const CategoryPage: React.FC = () => {
  const { slug } = useParams<{ slug: string }>()

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            หมวดหมู่: {slug || 'ไม่ระบุ'}
          </h1>
          <p className="text-xl text-gray-600">
            บทความทั้งหมดในหมวดหมู่นี้
          </p>
        </div>

        {/* Category Articles */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {[1, 2, 3].map((index) => (
            <div key={index} className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow">
              <div className="h-48 bg-gray-200 flex items-center justify-center">
                <span className="text-gray-500">รูปภาพบทความ</span>
              </div>
              <div className="p-6">
                <span className="inline-block bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded-full mb-3">
                  {slug}
                </span>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">
                  บทความในหมวด {slug} #{index}
                </h3>
                <p className="text-gray-600 mb-4">
                  สรุปเนื้อหาบทความในหมวดหมู่นี้ที่น่าสนใจและเป็นประโยชน์...
                </p>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-500">5 นาทีในการอ่าน</span>
                  <a 
                    href={`/articles/${slug}-article-${index}`}
                    className="text-blue-600 hover:text-blue-800 font-medium"
                  >
                    อ่านต่อ →
                  </a>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Empty State */}
        {(!slug || slug === 'empty') && (
          <div className="text-center py-12">
            <div className="bg-white rounded-lg shadow-md p-8 max-w-md mx-auto">
              <svg className="w-16 h-16 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">ไม่มีบทความ</h3>
              <p className="text-gray-600">
                ยังไม่มีบทความในหมวดหมู่นี้ กลับไปดูบทความอื่นๆ
              </p>
              <a 
                href="/articles"
                className="inline-block mt-4 bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors"
              >
                ดูบทความทั้งหมด
              </a>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default CategoryPage 