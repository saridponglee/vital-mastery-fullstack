import React from 'react'
import { useParams } from 'react-router-dom'

const ArticleDetailPage: React.FC = () => {
  const { slug } = useParams<{ slug: string }>()

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Article Header */}
        <div className="bg-white rounded-lg shadow-md overflow-hidden mb-8">
          <div className="h-64 bg-gray-200 flex items-center justify-center">
            <span className="text-gray-500">รูปภาพหลักของบทความ</span>
          </div>
          <div className="p-8">
            <h1 className="text-4xl font-bold text-gray-900 mb-4">
              {slug ? `บทความ: ${slug}` : 'ชื่อบทความ'}
            </h1>
            <div className="flex items-center text-sm text-gray-500 mb-6">
              <span>โดย ผู้เขียน</span>
              <span className="mx-2">•</span>
              <span>เผยแพร่เมื่อ 1 มกราคม 2025</span>
              <span className="mx-2">•</span>
              <span>5 นาทีในการอ่าน</span>
            </div>
          </div>
        </div>

        {/* Article Content */}
        <div className="bg-white rounded-lg shadow-md p-8 prose prose-lg max-w-none">
          <p>
            นี่คือเนื้อหาตัวอย่างของบทความ Lorem ipsum dolor sit amet, consectetur adipiscing elit. 
            Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, 
            quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.
          </p>

          <h2>หัวข้อย่อย</h2>
          <p>
            Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. 
            Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
          </p>

          <p>
            Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium, 
            totam rem aperiam, eaque ipsa quae ab illo inventore veritatis et quasi architecto beatae vitae dicta sunt.
          </p>

          <h3>หัวข้อย่อยย่อย</h3>
          <ul>
            <li>รายการที่ 1</li>
            <li>รายการที่ 2</li>
            <li>รายการที่ 3</li>
          </ul>

          <p>
            At vero eos et accusamus et iusto odio dignissimos ducimus qui blanditiis praesentium voluptatum 
            deleniti atque corrupti quos dolores et quas molestias excepturi sint occaecati cupiditate non provident.
          </p>
        </div>

        {/* Related Articles */}
        <div className="mt-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">บทความที่เกี่ยวข้อง</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {[1, 2].map((index) => (
              <div key={index} className="bg-white rounded-lg shadow-md overflow-hidden">
                <div className="h-32 bg-gray-200 flex items-center justify-center">
                  <span className="text-gray-500">รูปภาพ</span>
                </div>
                <div className="p-4">
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">
                    บทความที่เกี่ยวข้อง {index}
                  </h3>
                  <p className="text-gray-600 text-sm mb-3">
                    สรุปเนื้อหาบทความที่เกี่ยวข้อง...
                  </p>
                  <a 
                    href={`/articles/related-article-${index}`}
                    className="text-blue-600 hover:text-blue-800 font-medium text-sm"
                  >
                    อ่านต่อ →
                  </a>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

export default ArticleDetailPage 