// 获取最新新闻API（前端调用）
import { kv } from '@vercel/kv';

export default async function handler(req, res) {
  // 设置CORS头，允许前端访问
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
  res.setHeader('Cache-Control', 's-maxage=60, stale-while-revalidate=300');
  
  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  try {
    // 从KV存储获取最新新闻
    const stored = await kv.get('latest_news');
    
    if (!stored) {
      // 如果没有数据，触发一次更新
      return res.status(200).json({
        data: [],
        updatedAt: null,
        message: '数据更新中，请稍后再试',
        isUpdating: true
      });
    }
    
    const newsData = typeof stored === 'string' ? JSON.parse(stored) : stored;
    
    // 计算距离上次更新多久
    const lastUpdate = new Date(newsData.updatedAt);
    const now = new Date();
    const minutesAgo = Math.floor((now - lastUpdate) / 60000);
    
    res.status(200).json({
      ...newsData,
      minutesAgo,
      nextUpdateIn: Math.max(0, 10 - (minutesAgo % 10)),
      totalSources: 3
    });
    
  } catch (error) {
    console.error('Fetch error:', error);
    res.status(500).json({ 
      error: '获取新闻失败',
      message: error.message 
    });
  }
}