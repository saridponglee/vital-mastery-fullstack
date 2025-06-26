import React from 'react'
import { Link } from 'react-router-dom'

const NotFoundPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center py-12">
      <div className="max-w-md w-full text-center">
        <div className="bg-white rounded-lg shadow-md p-8">
          {/* 404 Icon */}
          <div className="w-24 h-24 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-6">
            <span className="text-4xl font-bold text-red-600">404</span>
          </div>

          <h1 className="text-3xl font-bold text-gray-900 mb-4">
            ไม่พบหน้าที่คุณต้องการ
          </h1>
          
          <p className="text-gray-600 mb-8">
            ขออภัย หน้าเว็บที่คุณกำลังมองหาอาจถูกย้าย ลบ หรือไม่เคยมีอยู่จริง
          </p>

          <div className="space-y-4">
            <Link 
              to="/"
              className="block w-full bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors"
            >
              กลับหน้าแรก
            </Link>
            
            <Link 
              to="/articles"
              className="block w-full bg-gray-100 text-gray-700 px-6 py-3 rounded-lg font-semibold hover:bg-gray-200 transition-colors"
            >
              ดูบทความทั้งหมด
            </Link>
          </div>

          <div className="mt-8 pt-6 border-t border-gray-200">
            <p className="text-sm text-gray-500">
              หากคุณมั่นใจว่า URL ถูกต้อง กรุณาติดต่อเราได้
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default NotFoundPage 