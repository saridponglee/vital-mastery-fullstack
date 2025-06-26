import { Routes, Route } from 'react-router-dom'
import { Helmet } from 'react-helmet-async'
import Layout from './components/layout/Layout'
import HomePage from './pages/HomePage'
import ArticlesPage from './pages/ArticlesPage'
import ArticleDetailPage from './pages/ArticleDetailPage'
import CategoryPage from './pages/CategoryPage'
import NotFoundPage from './pages/NotFoundPage'

function App() {
  return (
    <>
      <Helmet>
        <html lang="th" />
        <title>VITAL MASTERY</title>
        <meta name="description" content="VITAL MASTERY - แพลตฟอร์มเนื้อหาไทยที่มีการออกแบบทันสมัยและประสบการณ์การอ่านที่ยอดเยี่ยม" />
        <meta property="og:title" content="VITAL MASTERY" />
        <meta property="og:description" content="แพลตฟอร์มเนื้อหาไทยที่มีการออกแบบทันสมัยและประสบการณ์การอ่านที่ยอดเยี่ยม" />
        <meta property="og:type" content="website" />
        <meta property="og:locale" content="th_TH" />
      </Helmet>

      <div className="App min-h-screen bg-gray-50">
        <Layout>
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/articles" element={<ArticlesPage />} />
            <Route path="/articles/:slug" element={<ArticleDetailPage />} />
            <Route path="/category/:slug" element={<CategoryPage />} />
            <Route path="*" element={<NotFoundPage />} />
          </Routes>
        </Layout>
      </div>
    </>
  )
}

export default App 