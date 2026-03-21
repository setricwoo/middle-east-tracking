# ISW 战局翻译配置指南

## 当前问题
MyMemory 免费翻译 API 质量较差，军事术语翻译不准确。

## 推荐方案（已集成）

### 方案1：DeepL Free（推荐）⭐
**翻译质量最好，军事术语准确**

- **费用**：完全免费，每月 500,000 字符
- **质量**：专业级翻译，军事术语准确
- **设置难度**：简单

**设置步骤**：

1. 访问 https://www.deepl.com/pro-api 注册免费账户
2. 在账户页面获取 API Key（格式如：`xxx-xxx-xxx:fx`）
3. 在 GitHub 仓库设置环境变量：
   - 进入仓库 Settings → Secrets and variables → Actions
   - 点击 "New repository secret"
   - Name: `DEEPL_API_KEY`
   - Value: 你的 DeepL API Key
   - 点击 "Add secret"

4. 下次 GitHub Actions 运行时自动使用 DeepL 翻译

### 方案2：Hugging Face（无需注册）
**完全免费，无需 API Key**

- **费用**：完全免费
- **质量**：中等，比 MyMemory 好
- **限制**：可能有速率限制

**使用方法**：
无需任何设置，脚本会自动使用 Helsinki-NLP/opus-mt-en-zh 模型。

如需提高速率限制，可注册 Hugging Face 获取 Token：
1. 访问 https://huggingface.co/join 注册
2. 获取 Access Token
3. 在 GitHub Secrets 中添加 `HF_API_KEY`

## 翻译优先级

脚本按以下优先级选择翻译引擎：

1. **DeepL**（如果设置了 `DEEPL_API_KEY`）
2. **Hugging Face**（免费，无需配置）
3. **MyMemory**（回退方案）

## 验证翻译质量

查看最近的 ISW 更新，对比翻译效果：
- 原文：Key Takeaways
- DeepL 翻译：更准确、专业
- Hugging Face：流畅但可能有些术语不够精准

## 故障排除

### DeepL 配额用完
如果看到日志：`[DeepL 失败] ... 尝试 Hugging Face...`
表示 DeepL 每月 50 万字符配额已用完，会自动切换到 Hugging Face。

### 翻译太慢
Hugging Face 模型首次加载可能需要 10-20 秒（冷启动），后续请求会快很多。

### 完全不翻译
检查 GitHub Actions 日志中的错误信息，确保网络连接正常。
