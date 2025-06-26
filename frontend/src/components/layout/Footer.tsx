import React from 'react'

const Footer: React.FC = () => {
  const currentYear = new Date().getFullYear()

  return (
    <footer className="bg-gray-900 text-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {/* Brand */}
          <div>
            <h3 className="text-xl font-bold mb-4">VITAL MASTERY</h3>
            <p className="text-gray-300 text-sm">
              แพลตฟอร์มเนื้อหาไทยที่มีการออกแบบทันสมัยและประสบการณ์การอ่านที่ยอดเยี่ยม
            </p>
          </div>

          {/* Quick Links */}
          <div>
            <h4 className="text-lg font-semibold mb-4">ลิงก์ด่วน</h4>
            <ul className="space-y-2 text-gray-300">
              <li>
                <a href="/" className="hover:text-white transition-colors">หน้าแรก</a>
              </li>
              <li>
                <a href="/articles" className="hover:text-white transition-colors">บทความ</a>
              </li>
            </ul>
          </div>

          {/* Contact */}
          <div>
            <h4 className="text-lg font-semibold mb-4">ติดต่อเรา</h4>
            <p className="text-gray-300 text-sm">
              สำหรับข้อมูลเพิ่มเติมหรือข้อเสนอแนะ
            </p>
          </div>
        </div>

        <div className="border-t border-gray-700 mt-8 pt-8 text-center">
          <p className="text-gray-400 text-sm">
            © {currentYear} VITAL MASTERY. สงวนลิขสิทธิ์.
          </p>
        </div>
      </div>
    </footer>
  )
}

export default Footer 