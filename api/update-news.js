// 每10分钟自动执行：搜索最新中东新闻并存储
import { kv } from '@vercel/kv';

// 配置新闻源API（你可以替换为任何新闻API）
const NEWS_SOURCES = [
  {
    name: 'NewsAPI',
    url: 'https://newsapi.org/v2/everything',
    params: {
      q: '中东 OR 伊朗 OR 以色列 OR 霍尔木兹海峡 OR Middle East OR Iran OR Israel',
      language: 'zh',
      sortBy: 'publishedAt',
      pageSize: 20,
      apiKey: process.env.NEWS_API_KEY // 需要在Vercel环境变量中设置
    }
  }
];

export default async function handler(req, res) {
  // 验证Cron请求（Vercel自动添加Header）
  const isCron = req.headers['user-agent']?.includes('vercel-cron') || 
                 req.query.manual === 'true';
  
  if (!isCron && req.method !== 'POST') {
    return res.status(403).json({ error: 'Forbidden' });
  }

  try {
    console.log('Starting news update at:', new Date().toISOString());
    
    // 获取新闻（这里使用模拟数据演示，实际使用时取消注释下面的fetch代码）
    const newsData = await fetchLatestNews();
    
    // 存储到Vercel KV（键值存储）
    await kv.set('latest_news', JSON.stringify({
      data: newsData,
      updatedAt: new Date().toISOString(),
      source: 'auto-update'
    }));
    
    // 同时存储历史记录（最近100条）
    const history = await kv.get('news_history') || [];
    history.unshift({
      time: new Date().toISOString(),
      count: newsData.length
    });
    if (history.length > 100) history.pop();
    await kv.set('news_history', history);
    
    console.log(`Updated ${newsData.length} news items`);
    
    res.status(200).json({ 
      success: true, 
      updatedAt: new Date().toISOString(),
      count: newsData.length 
    });
    
  } catch (error) {
    console.error('Update failed:', error);
    res.status(500).json({ 
      success: false, 
      error: error.message 
    });
  }
}

// 获取最新新闻的函数
async function fetchLatestNews() {
  // 方案1：使用NewsAPI（推荐，稳定合法）
  if (process.env.NEWS_API_KEY) {
    try {
      const response = await fetch(
        `https://newsapi.org/v2/everything?q=中东+伊朗+以色列+霍尔木兹&language=zh&sortBy=publishedAt&pageSize=20&apiKey=${process.env.NEWS_API_KEY}`
      );
      const data = await response.json();
      if (data.articles) {
        return data.articles.map(article => ({
          title: article.title,
          summary: article.description,
          url: article.url,
          source: article.source.name,
          publishedAt: article.publishedAt,
          type: categorizeNews(article.title + article.description)
        }));
      }
    } catch (e) {
      console.log('NewsAPI fetch failed, using fallback');
    }
  }
  
  // 方案2：模拟数据（用于测试）
  return generateMockNews();
}

// 新闻分类
function categorizeNews(text) {
  const lower = text.toLowerCase();
  if (lower.includes('油价') || lower.includes('原油') || lower.includes('能源')) return 'energy';
  if (lower.includes('军事') || lower.includes('打击') || lower.includes('导弹')) return 'military';
  if (lower.includes('外交') || lower.includes('谈判') || lower.includes('协议')) return 'diplomacy';
  if (lower.includes('航运') || lower.includes('海峡') || lower.includes('港口')) return 'shipping';
  return 'general';
}

// 模拟数据生成器（用于测试）
function generateMockNews() {
  const now = new Date();
  return [
    {
      title: `美伊冲突最新进展：霍尔木兹海峡局势更新 ${now.toLocaleTimeString()}`,
      summary: '实时追踪中东地区最新军事动态和能源市场影响...',
      url: '#',
      source: '实时追踪系统',
      publishedAt: now.toISOString(),
      type: 'military'
    },
    {
      title: `油价最新行情：布伦特原油走势 ${now.toLocaleTimeString()}`,
      summary: '受中东局势影响，国际油价波动加剧...',
      url: '#',
      source: '能源市场监测',
      publishedAt: new Date(now - 5*60000).toISOString(),
      type: 'energy'
    }
  ];
}