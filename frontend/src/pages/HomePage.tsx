import React from 'react'

const HomePage: React.FC = () => {
  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="bg-gradient-to-r from-blue-600 to-purple-700 text-white py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h1 className="text-4xl md:text-6xl font-bold mb-6">
            VITAL MASTERY
          </h1>
          <p className="text-xl md:text-2xl mb-8 max-w-3xl mx-auto">
            แพลตฟอร์มเนื้อหาไทยที่มีการออกแบบทันสมัยและประสบการณ์การอ่านที่ยอดเยี่ยม
          </p>
          <a 
            href="/articles" 
            className="inline-block bg-white text-blue-600 px-8 py-3 rounded-lg font-semibold text-lg hover:bg-gray-100 transition-colors"
          >
            เริ่มอ่านบทความ
          </a>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              ทำไมต้องเลือก VITAL MASTERY?
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              เราให้ความสำคัญกับคุณภาพของเนื้อหาและประสบการณ์การใช้งานที่ดีที่สุด
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="text-center p-6">
              <div className="bg-blue-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">เนื้อหาคุณภาพสูง</h3>
              <p className="text-gray-600">บทความที่คัดสรรและตรวจสอบคุณภาพอย่างละเอียด</p>
            </div>

            <div className="text-center p-6">
              <div className="bg-green-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">ออกแบบเพื่อผู้อ่าน</h3>
              <p className="text-gray-600">ประสบการณ์การอ่านที่สบายตาและใช้งานง่าย</p>
            </div>

            <div className="text-center p-6">
              <div className="bg-purple-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">อัปเดตต่อเนื่อง</h3>
              <p className="text-gray-600">เนื้อหาใหม่ๆ ที่น่าสนใจอยู่เสมอ</p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="bg-gray-50 py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">
            พร้อมเริ่มต้นแล้วหรือยัง?
          </h2>
          <p className="text-xl text-gray-600 mb-8">
            สำรวจบทความที่น่าสนใจและเติมเต็มความรู้ของคุณ
          </p>
          <a 
            href="/articles" 
            className="inline-block bg-blue-600 text-white px-8 py-3 rounded-lg font-semibold text-lg hover:bg-blue-700 transition-colors"
          >
            ดูบทความทั้งหมด
          </a>
        </div>
      </section>
    </div>
  )
}

export default HomePage 