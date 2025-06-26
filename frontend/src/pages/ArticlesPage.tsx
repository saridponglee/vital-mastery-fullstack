import React from 'react'

const ArticlesPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">บทความทั้งหมด</h1>
          <p className="text-xl text-gray-600">
            สำรวจเนื้อหาที่น่าสนใจและเติมเต็มความรู้ของคุณ
          </p>
        </div>

        {/* Articles Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {/* Sample Article Cards */}
          {[1, 2, 3, 4, 5, 6].map((index) => (
            <div key={index} className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow">
              <div className="h-48 bg-gray-200 flex items-center justify-center">
                <span className="text-gray-500">รูปภาพบทความ</span>
              </div>
              <div className="p-6">
                <h3 className="text-xl font-semibold text-gray-900 mb-2">
                  ชื่อบทความตัวอย่าง {index}
                </h3>
                <p className="text-gray-600 mb-4">
                  สรุปเนื้อหาบทความที่น่าสนใจและเป็นประโยชน์สำหรับผู้อ่าน...
                </p>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-500">5 นาทีในการอ่าน</span>
                  <a 
                    href={`/articles/sample-article-${index}`}
                    className="text-blue-600 hover:text-blue-800 font-medium"
                  >
                    อ่านต่อ →
                  </a>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Load More Button */}
        <div className="text-center mt-12">
          <button className="bg-blue-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors">
            โหลดบทความเพิ่มเติม
          </button>
        </div>
      </div>
    </div>
  )
}

export default ArticlesPage 