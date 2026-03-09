# 实时新闻更新指南

## 📋 文件说明

- `news.html` - 实时新闻页面（静态）
- `NEWS_DATA` - 页面内的 JavaScript 数据对象，需要手动更新

## 🔄 更新步骤（每10分钟）

### 1. 搜索最新新闻

访问以下网站搜索"中东"、"美以伊"、"霍尔木兹"等关键词：

| 网站 | 网址 | source代码 |
|------|------|-----------|
| 财联社 | https://www.cls.cn/subject/10986 | cls |
| 金十数据 | https://www.jin10.com/ | jin10 |
| 新浪财经 | https://finance.sina.com.cn/ | sina |
| 华尔街见闻 | https://wallstreetcn.com/ | wallstreet |
| 21财经 | https://www.21cbh.com/ | 21cbh |

### 2. 编辑 news.html

打开 `news.html` 文件，找到 `NEWS_DATA` 对象（约第350行）。

### 3. 添加新新闻

在 `news` 数组**最前面**添加新条目：

```javascript
const NEWS_DATA = {
    "updateTime": "2026-03-09 15:30",  // 修改更新时间
    "news": [
        {
            "id": "7",  // 新ID（递增）
            "title": "新闻标题",
            "summary": "新闻摘要...",
            "source": "cls",  // 来源代码
            "sourceName": "财联社",  // 来源中文名
            "category": "energy",  // 分类：military/energy/shipping/diplomacy/market
            "time": "10分钟前",  // 相对时间
            "url": "https://原文链接"
        },
        // ... 旧新闻保留
    ]
};
```

### 4. 分类说明

| category | 含义 | 用途 |
|----------|------|------|
| military | 军事动态 | 战争、打击、导弹等 |
| energy | 能源市场 | 油价、产量、减产等 |
| shipping | 航运通道 | 霍尔木兹、航线、保险等 |
| diplomacy | 外交斡旋 | 谈判、制裁、声明等 |
| market | 金融市场 | 股市、黄金、汇率等 |

### 5. 保存并上传

1. 保存 `news.html`
2. 推送到 GitHub：
   ```bash
   git add news.html
   git commit -m "更新实时新闻 - 2026-03-09 15:30"
   git push
   ```
3. Netlify 会自动部署更新

## 💡 快速更新模板

复制以下模板，修改内容即可：

```javascript
{
    "id": "新的数字",
    "title": "这里写新闻标题",
    "summary": "这里写新闻摘要，2-3句话",
    "source": "cls",
    "sourceName": "财联社",
    "category": "energy",
    "time": "10分钟前",
    "url": "https://www.cls.cn/..."
}
```

## ⚠️ 注意事项

1. **不要删除旧新闻** - 页面设计为累积展示，旧新闻会自动保留
2. **ID要唯一** - 每条新闻的id不能重复
3. **时间格式** - updateTime使用 "YYYY-MM-DD HH:mm" 格式
4. **相对时间** - time字段使用"X分钟前"、"X小时前"等相对时间

## 🎯 自动化建议

如果手动更新太麻烦，建议：

1. 使用 RSS 聚合工具（如 Feedly）监控上述网站
2. 每10分钟查看一次新内容
3. 复制标题和摘要到模板中

或者考虑使用新闻API（如 NewsAPI）自动获取，但需要后端支持。
