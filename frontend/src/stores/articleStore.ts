import { create } from 'zustand';
import { subscribeWithSelector } from 'zustand/middleware';

export interface Article {
  id: number;
  title: string;
  content: string;
  excerpt: string;
  slug: string;
  author: {
    id: number;
    username: string;
    first_name: string;
    last_name: string;
  };
  category: {
    id: number;
    name: string;
  } | null;
  featured_image: string | null;
  reading_time: number;
  publishedAt: string;
  language: string;
  meta_description: string;
}

interface ArticleStore {
  // State
  articles: Record<string, Article>;
  language: 'th' | 'en';
  connectionStatus: 'connected' | 'disconnected' | 'connecting' | 'error';
  isLoading: boolean;
  error: string | null;
  lastUpdateTime: Date | null;
  
  // Actions
  addArticle: (article: Article) => void;
  setLanguage: (lang: 'th' | 'en') => void;
  setConnectionStatus: (status: ArticleStore['connectionStatus']) => void;
  handleRealtimeUpdate: (data: any) => void;
  
  // Getters
  getArticlesByLanguage: (lang?: 'th' | 'en') => Article[];
}

export const useArticleStore = create<ArticleStore>()(
  subscribeWithSelector((set, get) => ({
    // Initial State
    articles: {},
    language: 'en',
    connectionStatus: 'connecting',
    isLoading: false,
    error: null,
    lastUpdateTime: null,

    // Actions
    addArticle: (article) => {
      set((state) => {
        const articleKey = `${article.id}_${article.language}`;
        return {
          articles: {
            ...state.articles,
            [articleKey]: article
          },
          lastUpdateTime: new Date()
        };
      });
    },

    setLanguage: (lang) => {
      set({ language: lang });
    },
    
    setConnectionStatus: (status) => {
      set({ connectionStatus: status });
    },

    handleRealtimeUpdate: (data) => {
      try {
        const article: Article = {
          id: data.id,
          title: data.title,
          content: data.content || '',
          excerpt: data.excerpt || '',
          slug: data.slug,
          author: data.author,
          category: data.category,
          featured_image: data.featured_image,
          reading_time: data.reading_time,
          publishedAt: data.published_at,
          language: data.language,
          meta_description: data.meta_description || ''
        };
        
        get().addArticle(article);
        console.log('Real-time article update processed:', article);
      } catch (error) {
        console.error('Failed to process real-time update:', error);
      }
    },

    // Getters
    getArticlesByLanguage: (lang) => {
      const targetLang = lang || get().language;
      return Object.values(get().articles)
        .filter(article => article.language === targetLang)
        .sort((a, b) => new Date(b.publishedAt).getTime() - new Date(a.publishedAt).getTime());
    }
  }))
); 