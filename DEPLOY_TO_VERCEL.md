# Vercel 实时新闻系统部署指南

## 📋 前置要求

1. **Vercel账号**: 前往 https://vercel.com/signup 注册（可用GitHub账号登录）
2. **NewsAPI Key**（可选）: 前往 https://newsapi.org/register 获取免费API Key
3. **Git**: 用于推送代码

---

## 🚀 部署步骤

### 步骤1: 安装 Vercel CLI

```bash
npm install -g vercel
```

### 步骤2: 登录 Vercel

```bash
vercel login
```

### 步骤3: 部署项目

在项目根目录执行：

```bash
vercel
```

按提示操作：
- 确认项目目录: `./`
- 选择 scope: 你的账号
- 项目名称: `middle-east-news-tracker`（或其他）
- 是否覆盖现有设置: 如果是首次部署选 `N`

### 步骤4: 配置环境变量

部署成功后，在 Vercel Dashboard 中设置环境变量：

1. 打开 https://vercel.com/dashboard
2. 点击你的项目
3. 进入 **Settings** → **Environment Variables**
4. 添加以下变量：

| 变量名 | 值 | 说明 |
|--------|-----|------|
| `NEWS_API_KEY` | 你的NewsAPI密钥 | 用于获取新闻（可选） |
| `KIMI_API_KEY` | 你的Kimi API密钥 | 如果有的话 |

### 步骤5: 配置 Vercel KV（存储）

1. 在 Vercel Dashboard 点击 **Storage**
2. 点击 **Create Database** → **KV**
3. 选择区域（建议选 ` Singapore` 或 `Washington, D.C.`）
4. 连接到你的项目

### 步骤6: 重新部署

```bash
vercel --prod
```

---

## ⏰ 验证定时任务

部署成功后：

1. 访问 `https://你的项目名.vercel.app/api/update-news?manual=true`
   - 看到 `{"success":true}` 表示更新成功

2. 访问主页面 `https://你的项目名.vercel.app`
   - 应该看到新闻列表（首次可能需要等待10分钟）

3. 在 Vercel Dashboard → **Functions** 查看执行日志

---

## 🔧 自定义配置

### 修改更新频率

编辑 `vercel.json` 中的 `crons` 部分：

```json
"crons": [
  {
    "path": "/api/update-news",
    "schedule": "*/10 * * * *"  // 每10分钟
    // 其他选项:
    // "0 * * * *"     = 每小时
    // "0 */6 * * *"   = 每6小时
    // "0 0 * * *"     = 每天0点
  }
]
```

### 添加更多新闻源

编辑 `api/update-news.js` 中的 `fetchLatestNews` 函数，添加：

```javascript
// 财联社RSS（示例）
const clsNews = await fetch('https://www.cls.cn/rss');
// 解析并合并...

// 百度新闻API（示例）
const baiduNews = await fetch('https://...');
```

---

## 💰 费用说明

**Vercel Hobby（免费）计划包含：**
- 每月 100GB 带宽
- 每月 1000 次 Function 执行（每10分钟 = 每天144次，每月约4320次）
  - ⚠️ **注意**: 免费额度可能不够每10分钟更新！
  - 建议：升级到 Pro ($20/月) 或改为每30分钟更新

**NewsAPI 免费版：**
- 每天 100 次请求
- 足够每10分钟更新（每天144次，超过限制）
- 建议：每15分钟更新 或 使用付费版

---

## 🆘 故障排查

### Function执行超时
- Vercel免费版限制10秒执行时间
- 如果搜索太慢会超时
- 解决：减少新闻源数量或使用更快的API

### 数据不更新
1. 检查 Functions 日志是否有错误
2. 手动触发测试: `/api/update-news?manual=true`
3. 检查KV数据库是否已连接

### 新闻数量少
- 默认使用模拟数据（没有NEWS_API_KEY时）
- 添加 NEWS_API_KEY 获取真实新闻

---

## 📱 访问地址

部署成功后，你的实时新闻网站地址：
```
https://middle-east-news-tracker-你的用户名.vercel.app
```

手机、电脑都可以访问，每10分钟自动更新！